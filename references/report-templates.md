# Report Templates

Choose the template that matches the question type from Phase 1.

## Table Formatting Rule

All Markdown tables MUST use the 3-dash spaced separator format `| --- | --- |`. Never use variable-width separators like `|------|--------|` — they cause table recognition failure in many parsers (Obsidian, VS Code preview, etc.). Each cell in the separator row must be exactly `---` (optionally with alignment colons: `:---`, `:---:`, `---:`).

---

## Search Strategy（所有模板通用）

```
## Search Strategy

### 检索流程
[Phase 2 全链路简述：首轮X组 → 自检 → 术语发现 → 审计（发现Y类缺口）→ 补充Z组 → 合并去重得N篇]

### 术语矩阵
| 概念 | 标准名 | 同义词/别名 | MeSH |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

### 检索式
**Q1 — [描述]** (PubMed 命中: N, 检索: N)
```
[完整 PubMed 语法]
```
[Q2-Qn 同上。补充查询标注来源：首轮 / 术语发现 / 审计补充]

### 汇总
| 查询 | 命中 | 检索 | 新增唯一 |
| --- | --- | --- | --- |
| Q1  | N    | N    | N        |
| ... | ...  | ...  | ...      |

参数：[retmax, sort, API配置]
质量限制：[仅摘要 / 全文覆盖比例]
检索难度；术语补充：[Phase 1c 判定 + Phase 2d 补充的术语]
```

---

## Template A — Comparison / Methodology

For questions asking "which is better" or comparing approaches.

```
# Literature Review: [Topic]

[插入 Search Strategy 通用节]

## Quantitative Comparison Table
| Metric | Option A | Option B | Source [层级] |
| --- | --- | --- | --- |
| ... | ... | ... | PMID: XXXX |

## Key Findings
Each article: Authors, Journal, Year | PMID | Study design
Key findings with effect sizes | Relevance | Limitations

## Synthesis and Conclusions
Direct answer with evidence strength ratings

## Evidence Gaps
What the literature does NOT tell us

## References
```

---

## Template B — Clinical Efficacy / Intervention

PICO-driven review.

```
# Literature Review: [Topic]

[插入 Search Strategy 通用节]

## Key Findings
PICO-structured with effect sizes, CIs, NNT where available

## Synthesis and Conclusions

## Evidence Gaps

## References
```

---

## Template C — Atlas / Resource

For cell atlas, omics resource, or database questions.

```
# Literature Review: [Topic]

[插入 Search Strategy 通用节]

## Resource Summary Table
| Resource | Coverage | Platform | Access | Key findings |
| --- | --- | --- | --- | --- |

## Detailed Findings
Per-resource details

## Synthesis and Recommendations
Which resource best fits the need, and why

## Evidence Gaps

## References
```

---

## Template D — General

Fallback for questions that don't fit A-C.

```
# Literature Review: [Topic]

[插入 Search Strategy 通用节]

## Key Findings
Per-article with evidence level tags

## Synthesis and Conclusions
Direct answer with evidence strength

## Evidence Gaps

## References
```

---

## Evidence Level Tags

Every factual claim must carry one of these tags:

| Tag | Meaning |
| --- | --- |
| `[全文-PMC]` | Direct quote from PMC full text |
| `[全文-DOI]` | Publisher page visible text |
| `[摘要]` | PubMed abstract only — **cannot support negative claims** |
| `[推理]` | This agent's cross-evidence inference |

Negation constraint: "X is not mentioned" requires `[全文-*]` evidence. With only `[摘要]`, write "PubMed abstract does not list X."
