"""Merge deduplicate and format PubMed search results from multiple queries.

Usage:
  python dedup_format.py <results_dir> <output_path>

Naming convention: any query named with prefix "broad_" (e.g. "broad_low_precision")
is automatically treated as the broad recall query — its unique papers (not found in
any other query) are filtered for omics-relevant keywords and reported as candidates
for manual review.
"""
import json, pathlib, sys, re

OMICS_PATTERN = (
    r"transcriptom|proteom|metabolom|lipidom|genom|epigenom|multi.?om|"
    r"single.?cell|scRNA|snRNA|snATAC|scATAC|CITE.?seq|"
    r"imagin.*mass|mass.*imagin|MALDI|spatial|spatially|"
    r"Visium|Xenium|MERFISH|seqFISH|Stereo-seq|CosMx|Slide-seq|DBiT|GeoMx|"
    r"CODEX|CyCIF|MIBI|IMC|in situ|chromatin|methylom|ATAC|CUT&Tag|Hi.?C"
)


def main():
    if len(sys.argv) < 3:
        print("Usage: dedup_format.py <results_dir> <output_path>")
        sys.exit(1)

    results_dir = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])

    seen = set()
    all_articles = []
    query_stats = {}
    pmid_sources = {}

    for f in sorted(results_dir.glob("*_results.json")):
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        qname = data["query_name"]
        query_stats[qname] = {
            "total_count": data["total_count"],
            "retrieved": data["retrieved_count"],
            "unique_added": 0
        }
        for art in data["articles"]:
            pid = art["pmid"]
            pmid_sources.setdefault(pid, set()).add(qname)
            if pid not in seen:
                seen.add(pid)
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
        print(f"  [{qn}] {qs['total_count']} total, {qs['retrieved']} retrieved, {qs['unique_added']} unique")

    # Require at least one broad query: name must contain "broad" (case-insensitive)
    broad_names = [n for n in query_stats if "broad" in n.lower()]
    if not broad_names:
        print("ERROR: No broad recall query found.")
        print("At least one query must contain 'broad' in its name (e.g. 'broad_low_precision').")
        print("See references/query-construction.md for the mandatory low-precision query rule.")
        sys.exit(1)

    kw_re = re.compile(OMICS_PATTERN, re.IGNORECASE)
    for bname in broad_names:
        broad_only = [pid for pid, sources in pmid_sources.items() if sources == {bname}]
        candidates = []
        for pid in broad_only:
            for art in all_articles:
                if art["pmid"] == pid:
                    combined = art.get("title", "") + " " + art.get("abstract", "")
                    if kw_re.search(combined):
                        candidates.append(art)
                    break

        total = query_stats[bname]["retrieved"]
        print(f"\n[broad query: {bname}] {total} retrieved → {len(broad_only)} unique → {len(candidates)} omics-relevant candidates")
        if candidates:
            cand_path = out_path.with_name(out_path.stem + "_candidates.json")
            with open(cand_path, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, ensure_ascii=False, indent=2)
            print(f"Candidates written to: {cand_path}")
            for c in candidates:
                print(f"  [PMID:{c['pmid']}] ({c.get('year','?')}) {c.get('title','')[:160]}")
        else:
            print("  No omics-relevant candidates — vocabulary coverage appears complete.")


if __name__ == "__main__":
    main()
