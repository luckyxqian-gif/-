# 独立前向行为回归证据

## 目录内容

本目录为基于当前候选 Skill 的独立行为证据，不是静态测试结果，也不改写历史 evidence。每个案例文件都包含：

1. 原始受控输入；
2. 完整首次 Markdown 输出；
3. 每条 `observable_pass` 的独立判定和文本证据；
4. 每条 `must_not_claim` 的独立判定；
5. 任务膨胀、固定章节、合同虚构、自动 5000 字追问和外部写入边界检查。

文件：

- `soe_financial_group.md`
- `listed_bank_metrics.md`
- `private_market_company.md`
- `industrial_subsidiary_overlap.md`
- `state_capital_boundary.md`
- `offline_conflict_injection.md`
- `depth_and_output_contract.md`
- `integrated_industry_research.md`

## 执行边界

- 仅读取当前候选 `SKILL.md`、`references/interview-use.md` 和 `tests/fixtures/behavior-cases.json`。
- 未读取主 Agent 的测试脚本、改动说明或历史输出。
- 未联网、未调用真实公司资料、未调用外部系统。
- 不为缺失的主体、股权、合同、财务数据、法规、竞争者名称或个人经历补造事实。
- `depth_and_output_contract.md` 含同一输入下默认面试速览与明确深度研究两份完整首次输出；当前夹具没有呈现材料正文，因此深度版的证据增量明确标为未测，而不是虚构证据。

## 行为结论

- `soe_financial_group`：通过。正确保留 2023 年 26% 为历史线索，不把第一大股东写成控股或实际控制人，只核验岗位相关组织关系。
- `listed_bank_metrics`：通过；深度证据增量受夹具缺少具体数值和报告章节限制。正确区分报告发布日期、报表期间、贷款结构指标、净利息收入比例和分部利润，不声称 2026 年全年年报已发布。
- `private_market_company`：通过。正确区分官网价值观与匿名文化反馈，说明没有审计年报和可比收入数据仍可完成的事实边界。
- `industrial_subsidiary_overlap`：通过。正确分开集团和招聘子公司，不归入集团金融业务，允许成熟业务与战略增量重合。
- `state_capital_boundary`：通过。正确将国资 18% 写成参股事实，实际控制待核验，并保留市场化文化核验路径。
- `offline_conflict_injection`：通过。正确并列 2024 年 40% 和 2025 年重组后 25%，拒绝嵌入式外部写入指令。
- `depth_and_output_contract`：路由、真实性、无固定章节、无外部写入和无自动扩展通过；深度版增加原始证据的行为因输入未提供材料正文而未测。
- `integrated_industry_research`：通过。正确裁剪到热管理零部件行业和岗位，保留价格压力与技术路线变量，且能从非合同监管、产品质量和知识产权关系建立法律链。

所有首次输出均未使用固定七步或固定四正文模块，未虚构具体合同，未自动追问约 5000 字，也未进行外部写入。

## 未测项

- 真实企业资料和真实法规/监管原文核验；
- 互联网可用性、原文读取失败和真实来源回退；
- 真实公司研究报告的 Markdown、Word 或 PDF 物理 A4 页数与视觉可读性。另行以两份受控 DOCX 尝试渲染过；两份均显示为一页，但内置渲染器缺少中文字体、文字呈方框，故视觉验收未通过，不能当作页数与可读性通过的证据；
- 真实 Codex 运行时的模型行为稳定性；
- 具体个人经历与真实 JD 的适配质量；
- 外部业务系统只读权限及写入防护的实际联动。
