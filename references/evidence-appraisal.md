# Evidence Appraisal Standards

Apply throughout screening and synthesis.

## Study Design Hierarchy

| Design | Weight |
| --- | --- |
| Systematic review / Meta-analysis | Highest |
| RCT | High |
| Cohort / Case-control | Moderate |
| Cross-sectional / Case series | Low |
| Expert opinion / Narrative review | Lowest |

## Quantitative Appraisal

- Prefer effect sizes and confidence intervals over p-values alone
- Check sample size and statistical power
- Note primary vs secondary outcomes (watch for outcome switching)
- Check ITT vs per-protocol analysis
- Replication across independent cohorts strengthens evidence

## Methodological Quality

- Funding sources and conflicts of interest
- Randomization and blinding (for intervention studies)
- Selection bias and confounding control (for observational studies)
- Platform and annotation validation (for atlas/resource papers)

## Source Level Modifiers

These modify the confidence of any claim regardless of study design:

| Evidence Level | Confidence | Can assert negation? |
| --- | --- | --- |
| `[全文-PMC]` | High | Yes |
| `[全文-DOI]` | Moderate-High | Yes |
| `[摘要]` | Moderate | **No** — absence in abstract ≠ absence in paper |
| `[推理]` | Low | No |

A claim supported by multiple independent `[全文-*]` sources carries the highest confidence. A claim from a single `[摘要]` source should be presented with explicit uncertainty.

## Tissue/Model Caveats

When evidence comes from a specific experimental system, note it:
- "Drug X reduced infarct size by 30% `[全文-PMC]` (mouse model; human efficacy unverified)"

## Domain-Specific Checks

**For methodology comparison questions:**
- Is the comparison head-to-head (same model, same conditions) or indirect?
- Was transduction/delivery efficiency controlled? Expression differences may reflect delivery, not promoter strength
- Sample size: n=3 per group is common but underpowered for quantitative comparison

**For atlas/resource questions:**
- Are cell type annotations validated (experimentally vs computationally only)?
- Does stated coverage match the user's tissue/region of interest?
- Is data actually accessible in usable formats?
