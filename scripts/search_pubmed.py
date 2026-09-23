"""NCBI E-utilities PubMed search and fetch with auto-pagination.

Usage: python search_pubmed.py <output_dir> <query_name> <query_term> [retmax] [sort]
  - output_dir: path to write results JSON
  - query_name: label for this query (e.g., "Q1_mechanism")
  - query_term: PubMed query string
  - retmax: max results to fetch per page (default 60)
  - sort: relevance | date (default relevance)

Auto-pagination: if total_count > retmax, automatically fetches all pages
up to MAX_TOTAL (default 5000). Set retmax explicitly to cap at a lower number.
"""
import requests, json, os, time, pathlib, sys, xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
MAX_TOTAL = 5000
_cfg_path = os.path.expanduser("~/.ncbi_config.json")
cfg = {}
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        cfg = json.load(f)
KEY = cfg.get("api_key", "")
EMAIL = cfg.get("email", "researcher@example.com")

session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))


def clean(text):
    for c in [' ', ' ', '‐', '‑', ' ']:
        text = text.replace(c, ' ')
    return text


def _p(extra):
    p = {"email": EMAIL}
    if KEY:
        p["api_key"] = KEY
    p.update(extra)
    return p


def esearch(term, retmax=60, retstart=0, sort="relevance"):
    time.sleep(1.0)
    r = session.get(f"{BASE}/esearch.fcgi", params=_p({
        "db": "pubmed", "term": term, "retmax": retmax,
        "retstart": retstart, "retmode": "json", "sort": sort
    }), timeout=30)
    r.raise_for_status()
    return r.json()["esearchresult"]


def efetch(ids):
    """Fetch articles in batches of 200 (NCBI limit per efetch call)."""
    all_articles = []
    batch_size = 200
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        time.sleep(1.0)
        r = session.get(f"{BASE}/efetch.fcgi", params=_p({
            "db": "pubmed", "id": ",".join(str(x) for x in batch),
            "retmode": "xml"
        }), timeout=30)
        r.raise_for_status()
        tree = ET.fromstring(r.content)
        all_articles.extend(parse_articles(tree))
    return all_articles


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
                "is_review": "Review" in pub_types, "pub_types": pub_types,
                "mesh_terms": mesh_terms
            })
        except Exception as e:
            print(f"  Parse error for article: {e}")
    return articles


def fetch_all_pages(qterm, retmax, sort, max_total=MAX_TOTAL):
    """Auto-paginate: fetch all results up to max_total."""
    result = esearch(qterm, retmax=min(retmax, 200), retstart=0, sort=sort)
    total_count = int(result.get("count", 0))
    first_page = result.get("idlist", [])

    if total_count == 0:
        return [], 0

    actual_fetch = min(total_count, max_total)
    if total_count <= len(first_page):
        all_ids = first_page
    else:
        all_ids = list(first_page)
        page_size = min(retmax, 200)
        for start in range(page_size, actual_fetch, page_size):
            result = esearch(qterm, retmax=page_size, retstart=start, sort=sort)
            page_ids = result.get("idlist", [])
            if not page_ids:
                break
            all_ids.extend(page_ids)

    articles = efetch(all_ids)
    return articles, total_count


def main():
    if len(sys.argv) < 4:
        print("Usage: search_pubmed.py <output_dir> <query_name> <query_term> [retmax] [sort]")
        sys.exit(1)

    out_dir = pathlib.Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    qname = sys.argv[2]
    qterm = sys.argv[3]
    retmax = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    sort = sys.argv[5] if len(sys.argv) > 5 else "relevance"

    articles, total_count = fetch_all_pages(qterm, retmax, sort)

    output = {
        "query_name": qname,
        "query_term": qterm,
        "total_count": total_count,
        "retrieved_count": len(articles),
        "articles": articles
    }

    out_path = out_dir / f"{qname}_results.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    truncated_note = ""
    if total_count > MAX_TOTAL:
        truncated_note = f" (capped at {MAX_TOTAL})"
    print(f"[{qname}] Total: {total_count} | Retrieved: {len(articles)}{truncated_note} | Written: {out_path}")


if __name__ == "__main__":
    main()
