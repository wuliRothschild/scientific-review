# Supplementary Sources Beyond PubMed

PubMed 是主检索库，但单库检索存在系统性盲区。本文件规定何时、如何补充其他来源。所有来源均为公开 API 或公开网页，无需账号。

## Europe PMC（预印本覆盖）

bioRxiv / medRxiv 等预印本不被 PubMed 收录。机制、图谱、方法、技术类问题（领域前沿移动快）必须补 Europe PMC 检索：

```bash
python scripts/search_europepmc.py <output_dir> <query_name> "<query_term>" [retmax] [sort]
```

- 查询语法为 Lucene 风格，常用字段：`TITLE_ABS:"x"`、`AUTH:"姓 名"`、`OPEN_ACCESS:y`、`SRC:PPR`（仅预印本）、`FIRST_PDATE:[2024-01-01 TO 2026-12-31]`
- 与 PubMed 查询共用同一术语矩阵，检索式从 PubMed 版本改写（`[TIAB]` → `TITLE_ABS:`，MeSH 词改为自由词或 `MESH_HEADING:"x"`）
- 结果与 PubMed 结果一并由 `dedup_format.py` 合并；同一工作的预印本与期刊版 DOI 不同，均保留，报告中标注预印本状态
- 预印本未经同行评审——引用时必须在参考文献表中标注 preprint，且不作为否定性声明的依据

## 试验注册库（临床疗效类强制）

临床疗效类问题必须查 ClinicalTrials.gov（`https://clinicaltrials.gov/search?term=...` 或 API v2 `https://clinicaltrials.gov/api/v2/studies?query.term=...`）：

- 核对已发表结局与注册结局是否一致（结局切换是常见偏倚来源）
- 已完成但长期未发表的试验是发表偏倚的直接证据，写入 Evidence Gaps

## 引文追溯（关键论文）

对筛选出的每篇关键论文做前向（被引）与后向（参考文献）追溯：

- OpenAlex API（无需密钥）：`https://api.openalex.org/works/doi:<DOI>` 取 `referenced_works` 与 `cited_by_api_url` 字段
- 追溯发现的文献若符合纳入标准，补入筛选池并在报告中注明来源为引文追溯

## 跨学科问题

问题涉及非生物医学领域（材料、计算方法、社会科学）时，PubMed / Europe PMC 覆盖不足——用 OpenAlex 自由检索（`https://api.openalex.org/works?search=...`）补充，并在报告的检索局限中声明覆盖边界。
