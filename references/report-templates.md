# Report Templates

Choose the template that matches the question type from Phase 1.

## Table Formatting Rule

All Markdown tables MUST use the 3-dash spaced separator format `| --- | --- |`. Never use variable-width separators like `|------|--------|` — they cause table recognition failure in many parsers (Obsidian, VS Code preview, etc.). Each cell in the separator row must be exactly `---` (optionally with alignment colons: `:---`, `:---:`, `---:`).

---

## Search Strategy（所有模板通用）

以学术方法学章节风格撰写，面向零背景读者，不叙述执行过程。

```
## Search Strategy

### 数据来源与检索流程
[数据库及覆盖范围（PubMed 主库；按问题类型补充 Europe PMC 预印本、试验注册库、引文追溯）、检索执行日期、各维度检索式组数、合并去重后篇数]

### 术语矩阵
| 概念 | 标准名 | 同义词/别名 | MeSH |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

### 检索式
**Q1 — [描述]** (PubMed 命中: N, 检索: N)
```
[完整 PubMed 语法]
```
[Q2-Qn 同上；注明各检索式覆盖的维度]

### 汇总
| 查询 | 数据库 | 命中 | 检索 | 新增唯一 |
| --- | --- | --- | --- | --- |
| Q1  | ...  | N    | N    | N        |
| ... | ...  | ...  | ...  | ...      |

### 检索局限
[数据库覆盖边界声明（如未覆盖 Embase/Scopus）、MeSH 标引滞后对近 1-2 年文献的影响、全文覆盖率 N/M（[仅摘要] 占比）、预印本证据占比]
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

## Research Groups（可选）
核心研究组谱系、技术路线、结论独立性（其他模板亦可加入）

## Synthesis and Conclusions
Direct answer with evidence strength

## Evidence Gaps

## References
```

---

## Evidence Level Tags

Every factual claim must carry one of these tags in the working draft:

| Tag | Meaning |
| --- | --- |
| `[全文-PMC]` | Direct quote from PMC full text |
| `[全文-DOI]` | Publisher page visible text |
| `[摘要]` | PubMed abstract only — **cannot support negative claims** |
| `[推理]` | This agent's cross-evidence inference |

Negation constraint: "X is not mentioned" requires `[全文-*]` evidence. With only `[摘要]`, write "PubMed abstract does not list X."

以上为工作稿与审计用的内部标签。导出最终报告时按 SKILL.md 5c 交付纯度规则转化：正文用引用编号，参考文献表逐条标注 PMID/DOI、全文或摘要层级、预印本状态——标签本身不出现在交付稿中。
