# scientific-review

一个用于系统性文献综述的 AI Agent skill：在 PubMed 上执行结构化检索，强制全文验证，并通过独立审计 Agent 循环保证结论可靠性。

An agent skill for systematic literature reviews on PubMed — with enforced full-text verification and independent audit loops.

## 功能概述

* **五阶段工作流**：问题分类与维度规划 → 查询构建与首轮审计 → 关键论文全文获取 → 筛选/阅读/综合 → 报告生成与终审。
* **术语发现循环**：从检索结果中迭代补全标准名/同义词/MeSH 词，避免术语偏差导致的系统性漏检。
* **独立审计 Agent**：检索策略审计与报告审计均由独立 Agent 执行，持对抗性默认假设，逐条核对事实声明。
* **证据分级标注**：所有事实声明强制标注证据层级（`[全文-PMC]` / `[全文-DOI]` / `[摘要]` / `[推理]`），摘要层证据禁止支撑否定性结论。
* **全文获取降级链**：PMC → Unpaywall 开放获取 → 出版商页面，穷尽后才允许标记 `[仅摘要]`。

## 目录结构

```
├── SKILL.md                          # skill 主定义（五阶段流程与执行规则）
├── references/
│   ├── query-construction.md         # PubMed 查询构建规则（字段标签、MeSH、broad 查询要求）
│   ├── deep-reading.md               # 全文深读指南（按问题类型的阅读优先级）
│   ├── evidence-appraisal.md         # 证据评判标准（研究设计层级、定量评估）
│   └── report-templates.md           # 报告模板（比较/临床/图谱/通用四类）
└── scripts/
    ├── search_pubmed.py              # NCBI E-utilities 检索与自动分页抓取
    └── dedup_format.py               # 多查询结果合并去重与 broad 查询校验
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
* 可选：在 `~/.ncbi_config.json` 中配置 NCBI API key 以提高速率限制：

  ```json
  {"api_key": "<your-ncbi-api-key>", "email": "<your-email>"}
  ```

  未配置时使用公共速率限制，邮箱默认为占位符。

## 许可证

[Apache License 2.0](LICENSE)
