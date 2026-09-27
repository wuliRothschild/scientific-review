"""Merge, deduplicate and format search results from multiple queries and sources.

Usage:
  python dedup_format.py <results_dir> <output_path> [candidate_keywords_regex]

Records are deduplicated by PMID, falling back to DOI (then title) for records
without one — e.g. preprints returned by Europe PMC.

Broad-query audit (enforced): at least one query name must contain "broad",
otherwise exit 1. Papers found only by broad queries are candidate additions to
the term matrix. If candidate_keywords_regex is given — build it from the Phase 2a
term matrix of the current review — candidates are filtered by it; otherwise all
broad-only papers are reported unfiltered for manual review.
"""
import json, pathlib, sys, re

PRINT_CAP = 30


def record_key(art):
    pmid = str(art.get("pmid") or "").strip()
    if pmid:
        return "pmid:" + pmid
    doi = (art.get("doi") or "").strip().lower()
    if doi:
        return "doi:" + doi
    return "title:" + (art.get("title") or "")[:80].lower()


def main():
    if len(sys.argv) < 3:
        print("Usage: dedup_format.py <results_dir> <output_path> [candidate_keywords_regex]")
        sys.exit(1)

    results_dir = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])
    kw_re = re.compile(sys.argv[3], re.IGNORECASE) if len(sys.argv) > 3 else None

    seen = set()
    all_articles = []
    query_stats = {}
    key_sources = {}

    for f in sorted(results_dir.glob("*_results.json")):
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        qname = data["query_name"]
        query_stats[qname] = {
            "database": data.get("database", "unknown"),
            "total_count": data["total_count"],
            "retrieved": data["retrieved_count"],
            "unique_added": 0
        }
        for art in data["articles"]:
            key = record_key(art)
            key_sources.setdefault(key, set()).add(qname)
            if key not in seen:
                seen.add(key)
                all_articles.append(art)
                query_stats[qname]["unique_added"] += 1

    output = {
        "total_unique": len(all_articles),
        "query_stats": query_stats,
        "articles": sorted(all_articles, key=lambda a: a.get("year", "0"), reverse=True)
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Merged {len(all_articles)} unique articles from {len(query_stats)} queries")
    print(f"Written to: {out_path}")
    for qn, qs in query_stats.items():
        print(f"  [{qn}] ({qs['database']}) {qs['total_count']} total, {qs['retrieved']} retrieved, {qs['unique_added']} unique")

    # Require at least one broad query: name must contain "broad" (case-insensitive)
    broad_names = [n for n in query_stats if "broad" in n.lower()]
    if not broad_names:
        print("ERROR: No broad recall query found.")
        print("At least one query must contain 'broad' in its name (e.g. 'broad_low_precision').")
        print("See references/query-construction.md for the mandatory low-precision query rule.")
        sys.exit(1)

    index = {record_key(a): a for a in all_articles}
    for bname in broad_names:
        broad_only = [k for k, sources in key_sources.items() if sources == {bname}]
        candidates = []
        for k in broad_only:
            art = index[k]
            combined = art.get("title", "") + " " + art.get("abstract", "")
            if kw_re is None or kw_re.search(combined):
                candidates.append(art)

        total = query_stats[bname]["retrieved"]
        label = "keyword-matched" if kw_re else "unfiltered"
        print(f"\n[broad query: {bname}] {total} retrieved → {len(broad_only)} unique to this query → {len(candidates)} {label} candidates")
        if kw_re is None and broad_only:
            print("  No keyword regex supplied — candidates are unfiltered.")
            print("  Pass a regex built from the Phase 2a term matrix as argument 3 to filter them.")
        if candidates:
            cand_path = out_path.with_name(out_path.stem + "_candidates.json")
            with open(cand_path, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, ensure_ascii=False, indent=2)
            print(f"Candidates written to: {cand_path}")
            for c in candidates[:PRINT_CAP]:
                print(f"  [PMID:{c.get('pmid') or '-'}] ({c.get('year','?')}) {c.get('title','')[:160]}")
            if len(candidates) > PRINT_CAP:
                print(f"  ... and {len(candidates) - PRINT_CAP} more (see candidates JSON)")
        else:
            print("  No candidates — vocabulary coverage appears complete.")


if __name__ == "__main__":
    main()
