"""NCBI E-utilities PubMed search and fetch with history-based stable pagination.

Usage: python search_pubmed.py <output_dir> <query_name> <query_term> [retmax] [sort]
  - output_dir: path to write results JSON
  - query_name: label for this query (e.g., "Q1_mechanism")
  - query_term: PubMed query string
  - retmax: cap on total records fetched (default MAX_TOTAL)
  - sort: relevance | date (default relevance)

The result set is frozen server-side via usehistory (WebEnv/QueryKey), so batched
efetch calls cannot drift, duplicate or drop records even under relevance sorting.
Rate limits follow NCBI policy: 3 req/s without an API key, 10 req/s with one
(configure ~/.ncbi_config.json as {"api_key": "...", "email": "..."}).
"""
import requests, json, os, time, pathlib, sys, xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
MAX_TOTAL = 5000
EFETCH_BATCH = 200

_cfg_path = os.path.expanduser("~/.ncbi_config.json")
cfg = {}
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        cfg = json.load(f)
KEY = cfg.get("api_key", "")
EMAIL = cfg.get("email", "researcher@example.com")

DELAY = 0.12 if KEY else 0.4

session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))


def clean(text):
    for c in [' ', ' ', '‐', '‑', ' ']:
        text = text.replace(c, ' ')
    return text


def _p(extra):
    p = {"email": EMAIL, "tool": "scientific_review"}
    if KEY:
        p["api_key"] = KEY
    p.update(extra)
    return p


def esearch_history(term, sort="relevance"):
    """Freeze the full result set on the NCBI history server."""
    time.sleep(DELAY)
    r = session.get(f"{BASE}/esearch.fcgi", params=_p({
        "db": "pubmed", "term": term, "retmax": 0,
        "retmode": "json", "sort": sort, "usehistory": "y"
    }), timeout=30)
    r.raise_for_status()
    res = r.json()["esearchresult"]
    return int(res.get("count", 0)), res.get("webenv"), res.get("querykey")


def efetch_batch(webenv, query_key, retstart, retmax):
    """Fetch one batch from the frozen history; tolerate transient XML corruption."""
    for attempt in range(3):
        time.sleep(DELAY)
        r = session.get(f"{BASE}/efetch.fcgi", params=_p({
            "db": "pubmed", "query_key": query_key, "WebEnv": webenv,
            "retstart": retstart, "retmax": retmax, "retmode": "xml"
        }), timeout=60)
        r.raise_for_status()
        try:
            return parse_articles(ET.fromstring(r.content))
        except ET.ParseError as e:
            if attempt == 2:
                print(f"  WARNING: batch retstart={retstart} unparsable after 3 attempts, skipped: {e}")
                return []
            time.sleep(2 * (attempt + 1))
    return []


def parse_articles(tree):
    articles = []
    for article in tree.findall(".//PubmedArticle"):
        try:
            pmid = article.find(".//PMID").text
            title_el = article.find(".//ArticleTitle")
            title = clean(title_el.text or "") if title_el is not None else ""
            journal = (article.find(".//Journal/Title").text or "")
            year_el = article.find(".//PubDate/Year")
            if year_el is None:
                year_el = article.find(".//PubDate/MedlineDate")
            year = year_el.text[:4] if year_el is not None and year_el.text else "N/A"
            abstract_el = article.find(".//AbstractText")
            if abstract_el is None:
                parts = article.findall(".//Abstract/AbstractText")
                abstract = " ".join([clean(a.text or "") for a in parts if a.text])
            else:
                abstract = clean(abstract_el.text or "")
            authors = []
            for auth in article.findall(".//Author"):
                ln = auth.find("./LastName")
                fn = auth.find("./ForeName")
                if ln is not None:
                    authors.append(f"{fn.text or ''} {ln.text or ''}".strip())
            doi_el = article.find(".//ArticleId[@IdType='doi']")
            doi = doi_el.text if doi_el is not None else ""
            pub_types = [pt.text for pt in article.findall(".//PublicationType") if pt.text]
            mesh_terms = [mh.find("./DescriptorName").text
                         for mh in article.findall(".//MeshHeading")
                         if mh.find("./DescriptorName") is not None]
            articles.append({
                "pmid": pmid, "title": title, "journal": journal, "year": year,
                "abstract": abstract, "authors": authors, "doi": doi,
                "is_review": "Review" in pub_types, "is_preprint": False,
                "pub_types": pub_types, "mesh_terms": mesh_terms,
                "source": "pubmed"
            })
        except Exception as e:
            print(f"  Parse error for article: {e}")
    return articles


def main():
    if len(sys.argv) < 4:
        print("Usage: search_pubmed.py <output_dir> <query_name> <query_term> [retmax] [sort]")
        sys.exit(1)

    out_dir = pathlib.Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    qname = sys.argv[2]
    qterm = sys.argv[3]
    retmax = int(sys.argv[4]) if len(sys.argv) > 4 else MAX_TOTAL
    sort = sys.argv[5] if len(sys.argv) > 5 else "relevance"

    total_count, webenv, qkey = esearch_history(qterm, sort)
    fetch_n = min(total_count, retmax, MAX_TOTAL)

    articles = []
    for start in range(0, fetch_n, EFETCH_BATCH):
        articles.extend(efetch_batch(webenv, qkey, start, min(EFETCH_BATCH, fetch_n - start)))

    output = {
        "query_name": qname,
        "query_term": qterm,
        "database": "pubmed",
        "total_count": total_count,
        "retrieved_count": len(articles),
        "articles": articles
    }

    out_path = out_dir / f"{qname}_results.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    truncated_note = ""
    if total_count > fetch_n:
        truncated_note = f" (capped at {fetch_n})"
    print(f"[{qname}] Total: {total_count} | Retrieved: {len(articles)}{truncated_note} | Written: {out_path}")


if __name__ == "__main__":
    main()
