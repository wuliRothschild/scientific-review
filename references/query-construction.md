# PubMed Query Construction

Build queries using these MeSH terms, field tags, and syntax rules.

## Field Tags

| Tag | Syntax | Example |
| --- | --- | --- |
| Title/Abstract | `term[Title/Abstract]` or `term[TIAB]` | `"ferroptosis"[TIAB]` |
| MeSH Terms | `term[MeSH Terms]` or `term[MeSH]` | `"Muscle, Skeletal"[MeSH]` |
| Title only | `term[Title]` or `term[TI]` | `"nuclear migration"[TI]` |
| Author | `name[Author]` or `name[AU]` | `Roman W[Author]` |
| Journal | `name[Journal]` or `name[TA]` | `Science[TA]` |
| Date range | `"YYYY"[DP] : "YYYY"[DP]` | `"2020"[DP]:"2026"[DP]` |
| Publication type | `type[PT]` | `Review[PT]` |

## Boolean Operators

- `AND`, `OR`, `NOT` — always uppercase
- Group with parentheses: `(A OR B) AND C`
- Combine synonym groups with OR, join concepts with AND

## Common MeSH Terms

| Concept | MeSH |
| --- | --- |
| Skeletal muscle | `"Muscle, Skeletal"[MeSH]` |
| Muscle injury | `"Muscle, Skeletal/injuries"[MeSH]` |
| Regeneration | `"Regeneration"[MeSH]` |
| Cell nucleus | `"Cell Nucleus"[MeSH]` |
| Signal transduction | `"Signal Transduction"[MeSH]` |

## Query Construction Pattern

```
(SynonymGroup1_OR) AND (SynonymGroup2_OR) AND ... [optional filters]
```

Among the queries constructed for a review, **at least one must be a low-precision/high-recall query**, named with `broad` in its query name (e.g. `broad_low_precision`). All other queries can be precision-oriented with specific technical vocabulary. `dedup_format.py` enforces this: exit 1 if no query name contains "broad".

**构建规则**：保留 core entities（基因/蛋白/药物/疾病/组织），将其余修饰词从当前最精确的层级退一级——平台名退到技术名，技术名退到概念描述词，概念描述词退到无修饰。不退化为单字通配。

**跨场景示例**：
```
// 临床疗效 — 退去研究设计限定词：
Precision: ("alendronate") AND ("osteoporosis"[MeSH]) AND ("RCT"[TIAB] OR "randomized"[TIAB])
Broad:     ("bisphosphonate*") AND ("osteoporosis" OR "bone density" OR "fracture")

// 机制通路 — 退去机制/通路限定词：
Precision: ("TP53") AND ("ferroptosis") AND ("signaling" OR "pathway")
Broad:     ("TP53" OR "p53") AND ("cell death" OR "ferroptosis" OR "apoptosis")

// 方法技术 — 技术术语退一级（平台名→技术名→概念词），不退化到通配：
Precision: ("Visium"[TIAB] OR "Xenium"[TIAB]) AND ("bone"[TIAB] OR "cartilage"[TIAB])
Broad:     ("spatially resolved"[TIAB] OR "spatial atlas"[TIAB]) AND ("bone"[TIAB] OR "cartilage"[TIAB])
```

Example — gene + tissue + mechanism:
```
("TP53"[TIAB] OR "p53"[TIAB] OR "tumor protein p53"[TIAB])
AND ("Breast Neoplasms"[MeSH] OR "breast cancer"[TIAB] OR "breast tumor"[TIAB])
AND ("ferroptosis"[TIAB] OR "apoptosis"[TIAB] OR "cell death"[TIAB])
```

## MeSH 时效性注意

新发表论文的 MeSH 标引有数月滞后。检索近 1-2 年文献时，MeSH 查询必须与 TIAB 同义词查询并行，不能单独依赖 MeSH，否则系统性漏掉最新成果。预印本无 MeSH 标引——预印本覆盖见 `references/multi-source.md`。

## Adaptive Replan Triggers

After initial search, check for these conditions before continuing:

1. **Zero/near-zero hits** → terminology likely wrong; expand synonym groups
2. **All hits from same research group** → field is niche; broaden to related concepts
3. **Hits don't match intent** → query captured homonym; add NOT operators
4. **Only one dimension represented** → other dimensions need dedicated queries
5. **Broad query contains unique papers absent from all precision queries** → unknown synonyms exist; extract their terminology, update the term matrix, and supplement precision queries
