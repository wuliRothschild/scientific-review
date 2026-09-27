"""Europe PMC REST search with cursor-based stable pagination.

Covers PubMed/PMC records and bioRxiv/medRxiv preprints (source=PPR), which
PubMed itself does not index. Output schema matches search_pubmed.py so results
from both merge cleanly with dedup_format.py.

Usage: python search_europepmc.py <output_dir> <query_name> <query_term> [retmax] [sort]
  - query_term: Europe PMC query syntax (Lucene-like), e.g.
      TITLE_ABS:"ferroptosis" AND OPEN_ACCESS:y
      SRC:PPR AND (TITLE_ABS:"spatial transcriptomics")   -- preprints only
      FIRST_PDATE:[2024-01-01 TO 2026-12-31] AND (...)
  - retmax: cap on total records fetched (default MAX_TOTAL)
  - sort: relevance | date (default relevance)

Cursor-based pagination (cursorMark) guarantees a stable result set across pages.
"""
import requests, json, time, pathlib, sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PAGE = 100
MAX_TOTAL = 5000
DELAY = 0.4

session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))


def clean(text):
    for c in [' ', ' ', '‐', '‑', ' ']:
        text = text.replace(c, ' ')
    return text


def fetch_page(qterm, cursor, sort):
    params = {
        "query": qterm, "format": "json", "pageSize": PAGE,
        "cursorMark": cursor, "resultType": "core",
    }
    if sort == "date":
        params["sort"] = "FIRST_PDATE_D desc"
    time.sleep(DELAY)
    r = session.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def map_article(hit):
    authors = [a.strip().rstrip(".") for a in (hit.get("authorString") or "").split(",") if a.strip()]
    pub_types = hit.get("pubTypeList", {}).get("pubType") or []
    mesh = [m.get("descriptorName", "") for m in
            (hit.get("meshHeadingList", {}).get("meshHeading") or [])]
    src = hit.get("source", "")
    is_preprint = src == "PPR" or "Preprint" in pub_types
    return {
        "pmid": hit.get("pmid") or "",
        "title": clean(hit.get("title") or ""),
        "journal": hit.get("journalTitle") or ("preprint" if is_preprint else ""),
        "year": str(hit.get("pubYear") or "N/A"),
        "abstract": clean(hit.get("abstractText") or ""),
        "authors": authors,
        "doi": hit.get("doi") or "",
        "is_review": "Review" in pub_types,
        "is_preprint": is_preprint,
        "pub_types": pub_types,
        "mesh_terms": mesh,
        "source": f"europepmc:{src}"
    }


def main():
    if len(sys.argv) < 4:
        print("Usage: search_europepmc.py <output_dir> <query_name> <query_term> [retmax] [sort]")
        sys.exit(1)

    out_dir = pathlib.Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    qname = sys.argv[2]
    qterm = sys.argv[3]
    retmax = int(sys.argv[4]) if len(sys.argv) > 4 else MAX_TOTAL
    sort = sys.argv[5] if len(sys.argv) > 5 else "relevance"

    cap = min(retmax, MAX_TOTAL)
    articles = []
    cursor = "*"
    total_count = None
    while len(articles) < cap:
        data = fetch_page(qterm, cursor, sort)
        if total_count is None:
            total_count = int(data.get("hitCount", 0))
        hits = data.get("resultList", {}).get("result", [])
        if not hits:
            break
        articles.extend(map_article(h) for h in hits)
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt

    articles = articles[:cap]
    total_count = total_count or 0

    output = {
        "query_name": qname,
        "query_term": qterm,
        "database": "europepmc",
        "total_count": total_count,
        "retrieved_count": len(articles),
        "articles": articles
    }

    out_path = out_dir / f"{qname}_results.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    truncated_note = f" (capped at {cap})" if total_count > cap else ""
    print(f"[{qname}] Total: {total_count} | Retrieved: {len(articles)}{truncated_note} | Written: {out_path}")


if __name__ == "__main__":
    main()
