# scientific-review

一个用于系统性文献综述的 AI Agent skill：以 PubMed 为主库执行结构化检索，覆盖预印本、试验注册库与引文追溯，强制全文验证，并通过独立审计 Agent 循环保证结论可靠性。

An agent skill for systematic literature reviews — PubMed-based structured search extended with preprints, trial registries and citation chasing, enforced full-text verification, and independent audit loops.

## 功能概述

* **五阶段工作流**：问题分类与维度规划 → 查询构建与首轮审计 → 关键论文全文获取 → 筛选/阅读/综合 → 报告生成与终审。各阶段严格串行、双审计门强制；阶段内独立的机械性操作可并行。
* **多源检索**：PubMed（usehistory 服务端冻结结果集，翻页不漂移）为主；按问题类型强制补充 Europe PMC 预印本、ClinicalTrials.gov 注册结局核对、OpenAlex 引文追溯。
* **术语发现循环**：从检索结果中迭代补全标准名/同义词/MeSH 词，避免术语偏差导致的系统性漏检；MeSH 标引滞后对近年文献的影响有显式防护。
* **独立审计 Agent**：检索策略审计与报告审计均由独立 Agent 执行，持对抗性默认假设与独立信息源，逐条核对事实声明。
* **证据分级标注**：所有事实声明强制标注证据层级（`[全文-PMC]` / `[全文-DOI]` / `[摘要]` / `[推理]`），摘要层证据禁止支撑否定性结论；关键结论须经独立研究组印证检查。
* **全文获取降级链**：PMC → Unpaywall 开放获取 → 出版商页面 → 浏览器渲染兜底（按能力选择，不绑定特定工具），穷尽后才允许标记 `[仅摘要]`，并有全文覆盖率规则约束结论强度。
* **交付纯度**：证据标签等内部标记仅供工作稿与审计；导出报告为独立学术文档，面向零背景读者，正文引用编号 + 参考文献表逐条标注来源层级与预印本状态。

## 目录结构

```
├── SKILL.md                          # skill 主定义（五阶段流程与执行规则）
├── references/
│   ├── query-construction.md         # PubMed 查询构建规则（字段标签、MeSH、broad 查询要求）
│   ├── multi-source.md               # PubMed 之外的补充来源（预印本/注册库/引文追溯）
│   ├── deep-reading.md               # 全文深读指南（按问题类型的阅读优先级）
│   ├── evidence-appraisal.md         # 证据评判标准（研究设计层级、定量评估）
│   └── report-templates.md           # 报告模板（比较/临床/图谱/通用四类）
└── scripts/
    ├── search_pubmed.py              # NCBI E-utilities 检索（usehistory 稳定分页、自适应限速）
    ├── search_europepmc.py           # Europe PMC 检索（游标分页，覆盖 bioRxiv/medRxiv 预印本）
    └── dedup_format.py               # 多查询多来源合并去重（PMID/DOI 双键）与 broad 查询校验
```

## 安装

将本仓库目录复制到 agent 的 skills 目录即可，例如：

```bash
git clone https://github.com/wuliRothschild/scientific-review.git
cp -r scientific-review ~/.zcode/skills/   # 或你的 agent skills 目录
```

## 使用

在支持 skills 的 agent 中触发，例如：

```
/scientific-review <研究问题或主题>
```

或以自然语言提出系统性文献调研需求（如"系统性综述某基因在某疾病中的机制研究"），skill 会自动接管执行。

## 依赖

* Python 3（脚本需以 `python -X utf8` 运行）
* `requests` 库
* 可选：在 `~/.ncbi_config.json` 中配置 NCBI API key 以提高速率限制（3 req/s → 10 req/s）：

  ```json
  {"api_key": "<your-ncbi-api-key>", "email": "<your-email>"}
  ```

  未配置时使用公共速率限制，邮箱默认为占位符。

## 许可证

[Apache License 2.0](LICENSE)
