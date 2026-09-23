# Deep Reading Guide

Apply when reading full-text papers in Phase 4. Reading priority varies by question type.

## Reading Priority by Question Type

| 问题类型 | 先读 | 再读 | 常被忽略 |
| --- | --- | --- | --- |
| **机制/通路** | Results（图表、Western blot） | Discussion（模型） | Extended data figures |
| **临床疗效** | Results（表格、效应量） | Methods（随机化、盲法） | Supplementary appendices |
| **方法比较** | Methods（设计参数） | Results（定量对比） | Supplementary protocols |
| **图谱/资源** | Methods（平台、覆盖度） | Data availability | Cluster marker tables |
| **标记/稀有细胞** | Results（聚类注释、UMAP） | Methods（分类标准） | Marker gene lists in supplements |
| **技术/方案** | Methods（逐步步骤） | Troubleshooting / Notes | Supplementary reagent tables |

## Full-Text Extraction Checklist

For every paper read at full-text level, extract:

- **Quantitative findings** with effect sizes and confidence intervals — not just p-values
- **Specific methodological details**: reagents, doses, timepoints, platforms, sample sizes
- **Limitations stated by the authors** — note what they acknowledge they didn't prove
- **Data contradicting or nuancing the abstract**: does the full text hedge what the abstract claims?

## Methodology-Specific Checks

**For methodology comparison questions:**
- Is the comparison head-to-head (same model, same conditions) or indirect?
- Was transduction/delivery efficiency controlled? (Expression differences may reflect delivery, not function)
- Is sample size adequate for the comparison? (n=3 per group is common but underpowered)

**For atlas/resource questions:**
- Are cell type annotations validated (experimentally confirmed vs computational only)?
- Does stated coverage match the user's tissue/region of interest?
- Is data actually accessible in usable formats?
