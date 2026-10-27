import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCE = (ROOT / "references" / "interview-use.md").read_text(encoding="utf-8")
OPENAI_YAML = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CASES = json.loads((ROOT / "tests" / "fixtures" / "behavior-cases.json").read_text(encoding="utf-8"))


class SkillContractTests(unittest.TestCase):
    def test_scope_and_two_depths_are_explicit(self):
        self.assertIn("默认按 **完整基础研究** 执行", SKILL)
        self.assertIn("**深度法律行业研究**", SKILL)
        self.assertIn("不得自动改简历、模拟面试、预测录取、投递、创建外部记录", SKILL)

    def test_four_internal_stages_have_dependencies_and_completion_conditions(self):
        stages = [
            "### A. 确定主体及焦点",
            "### B. 形成行业—公司判断",
            "### C. 推导法律及岗位影响",
            "### D. 整合与验证",
        ]
        positions = [SKILL.index(stage) for stage in stages]
        self.assertEqual(positions, sorted(positions))
        for condition in ["完成条件（A 门）：", "完成条件（B 门）：", "完成条件（C 门）："]:
            self.assertIn(condition, SKILL)
        self.assertIn("D 门放行条件：", SKILL)
        self.assertIn("不要求固定检索轮数", SKILL)

    def test_research_gates_block_product_creation_until_release(self):
        for phrase in [
            "**待完成、已通过、证据受限**", "没有查到资料、还没研究、材料不充分，均不等于“不适用”",
            "只列公司项目、政策新闻、宣传口号或行业通识，不构成 B 门通过",
            "只罗列风险名称、法规名称和通用动作，不构成通过",
            "不得开始写正式报告正文、确定最终栏目、制作 HTML/DOCX/PDF/PPT 或进行版面压缩",
            "HTML 默认值与五页 A4 上限只规定研究完成后的呈现方式与阅读负担",
        ]:
            self.assertIn(phrase, SKILL)
        self.assertIn("可以在降低结论确定性后进入整合", SKILL)
        self.assertIn("不适用项均有任务范围理由", SKILL)

    def test_seven_content_categories_are_coverage_not_steps(self):
        for category in [
            "研究主体及组织定位", "行业基本面与竞争", "有实质影响的外部变量与趋势",
            "公司业务与发展", "业务法律与法务动作", "岗位与个人适配", "求职面试应用",
        ]:
            self.assertIn(category, SKILL)
        self.assertIn("不把它们变成七步、七个标题或七份文件", SKILL)
        self.assertIn("只研究与问题直接有关的类别", SKILL)

    def test_six_module_logic_is_preserved_without_fixed_headings(self):
        for phrase in [
            "企业主体与组织定位", "行业基本面与商业逻辑", "公司业务与竞争地位",
            "外部变化、趋势与战略", "业务法律问题与目标法务岗位", "个人适配与求职面试应用",
        ]:
            self.assertIn(phrase, SKILL)
        self.assertIn("不强制固定标题或章数", SKILL)
        self.assertNotIn("只有四个正文模块", SKILL)
        self.assertNotIn("四个正文模块", SKILL)

    def test_output_contract_is_compact_and_beginner_readable(self):
        self.assertIn("最多五张 A4", SKILL)
        self.assertIn("面向没有行业背景的读者", SKILL)
        self.assertIn("按信息逻辑组织自然小节或更直接的专题顺序", SKILL)
        self.assertIn("内部检索笔记、过程记录、测试日志和 AI 推理不进入", SKILL)
        self.assertIn("不得在交付后自动询问扩展约 5000 字", SKILL)
        self.assertNotIn("是否需要我在这份完整报告基础上整理或扩展为约 5000 字", SKILL)

    def test_sources_are_only_in_the_final_independent_html_room(self):
        self.assertIn("只在报告末尾作为唯一的独立“资料来源”板块", SKILL)
        self.assertIn("最后一个独立导航房间", SKILL)
        self.assertIn("正文不放来源列表、链接、检索说明或来源逐条解释", SKILL)

    def test_reader_first_business_to_legal_conversion_is_explicit(self):
        for phrase in [
            "**先解码核心业务。**", "谁是客户、为什么会付费，交易或收入怎样形成",
            "核心事实 → 业务机制 → 经营含义 → 法律或岗位含义",
            "业务环节、参与方、风险和法务动作连起来",
            "内部门禁、核验状态、检索过程和审计式措辞不得成为用户可见的标题",
            "**小白复述检验：**", "公司卖什么、谁为什么付费",
        ]:
            self.assertIn(phrase, SKILL)

    def test_delivery_format_routing_defaults_to_html_after_research_release(self):
        self.assertIn("默认最终交付一份完整 HTML 研究报告", SKILL)
        self.assertIn("用户无需重复说明“输出 HTML”", SKILL)
        self.assertIn("用户本轮明确指定 Markdown、DOCX 或其他格式时，该指定优先", SKILL)
        self.assertIn("只交付指定格式，不额外生成 HTML", SKILL)
        self.assertIn("其他普通任务仍按全局格式规则处理", SKILL)
        self.assertIn("在此之前不得启动正式 HTML 成品制作", SKILL)
        self.assertIn("`personal-html-delivery-cn`", SKILL)
        self.assertNotIn("默认交付一份完整 Markdown", SKILL)

    def test_industry_judgment_is_selective_and_preserves_data_boundaries(self):
        for phrase in [
            "不强制固定指标数", "不做四分位等统计", "PEST 四维扫描", "没有重要变量的维度不凑段落",
            "主体、报告期、定义、单位、分母、币种和来源", "不得冒充营业收入份额",
        ]:
            self.assertIn(phrase, SKILL)
        self.assertNotIn("确定每个行业真正运行的 3—5 个经营指标", SKILL)

    def test_industry_research_method_is_operational_not_a_heading_list(self):
        for phrase in [
            "产品/服务—客户—地域—产业链环节—时点", "还原行业怎样运转", "价值分配",
            "建立竞争判断", "直接竞争者、相邻竞争者、新进入者和替代方案",
            "选择并校验经营证据", "筛选外部变量与未来条件", "落到目标公司和岗位",
        ]:
            self.assertIn(phrase, SKILL)
        self.assertIn("不要求用户选择方法或提供分析框架", SKILL)

    def test_depth_scope_and_restored_research_capabilities_are_unambiguous(self):
        for phrase in [
            "法律专题、行业专题、公司速览或岗位理解只研究与问题直接有关的类别", "只运行回答该问题所必需的环节",
            "已正式发布的最新完整年报", "区分发布日期与报表/事实所属期间",
            "非上市或无公开年报时，改用可核验的工商、监管、公司业务、项目或交易资料",
            "市场规模、增长、供需变化和增长驱动", "成熟业务优先识别高频经营、持续合规与日常争议",
            "战略增量业务优先审查新准入、研发/IP、投资合作、出口/数据、产品责任",
            "国资参股不当然等于国企", "文件标题、发布日期、数据或事实所属期间、链接或材料位置",
            "实际读取范围、失败原因和待核验渠道",
        ]:
            self.assertIn(phrase, SKILL)

    def test_legal_chain_supports_non_contract_questions(self):
        self.assertIn("参与方与法律关系/监管对象", SKILL)
        self.assertIn("合同型问题再分析交易结构、合同和关键条款", SKILL)
        self.assertIn("不把“具体合同”当作通用必经环节", SKILL)
        self.assertIn("许可、数据、知识产权、劳动、公司治理", SKILL)
        self.assertNotIn("→ 具体合同 → 适用法律与监管", SKILL)

    def test_entity_evidence_and_safety_boundaries_are_retained(self):
        for phrase in [
            "第一大股东、控股股东、实际控制人分别证明", "不得推断行政级别或企业干部职级",
            "二者可以重合", "搜索摘要不替代已读原文", "不可信业务数据",
        ]:
            self.assertIn(phrase, SKILL)

    def test_reference_and_metadata_are_narrow_and_valid(self):
        self.assertEqual(SKILL.count("[行业理解的面试使用](references/interview-use.md)"), 1)
        self.assertIn("只在用户明确要求", REFERENCE)
        self.assertIn("行业选择理由、行业认同表达", REFERENCE)
        self.assertIn("不重做公司研究，不自动解锁未要求的面试工作", REFERENCE)
        self.assertIn("$job-industry-research-cn", OPENAI_YAML)
        self.assertNotIn("七步", OPENAI_YAML)
        self.assertNotIn("四章", OPENAI_YAML)

    def test_behavior_fixtures_keep_historical_boundaries_and_dense_synthesis_regression(self):
        historical_ids = {
            "soe_financial_group", "listed_bank_metrics", "private_market_company",
            "industrial_subsidiary_overlap", "state_capital_boundary", "offline_conflict_injection",
            "depth_and_output_contract", "integrated_industry_research",
        }
        expected_ids = historical_ids | {"dense_research_synthesis", "delivery_format_routing"}
        self.assertEqual({case["id"] for case in CASES}, expected_ids)
        self.assertEqual(len(CASES), 10)
        self.assertTrue(historical_ids <= {case["id"] for case in CASES})
        for case in CASES:
            self.assertTrue(case["fictional"])
            self.assertGreaterEqual(len(case["observable_pass"]), 3)
            self.assertGreaterEqual(len(case["must_not_claim"]), 2)
        flattened = "\n".join("\n".join(case["observable_pass"]) for case in CASES)
        for requirement in ["三页约束", "PEST变量", "非合同问题", "不自动写外部系统", "追问5000字"]:
            self.assertIn(requirement, flattened)

    def test_full_first_output_records_exist_for_all_controlled_cases(self):
        expected_ids = {case["id"] for case in CASES}
        behavior_runs = ROOT / "tests" / "behavior-runs"
        self.assertTrue((behavior_runs / "README.md").is_file())
        self.assertEqual(
            {path.stem for path in behavior_runs.glob("*.md")} - {"README"},
            expected_ids,
        )
        for case_id in expected_ids:
            record = (behavior_runs / f"{case_id}.md").read_text(encoding="utf-8")
            for heading in ["## 受控输入", "## 逐条验收判定", "### `must_not_claim`"]:
                self.assertIn(heading, record)
            self.assertTrue(
                "## 首次 Markdown 输出" in record or "## 首次 HTML 输出" in record,
                case_id,
            )

    def test_historical_evidence_is_preserved_as_baseline(self):
        evidence = ROOT / "tests" / "evidence"
        self.assertEqual(len(list(evidence.glob("a-*.md"))), 6)
        self.assertIn("约 5000 字", (evidence / "a-delivery-first-output.md").read_text(encoding="utf-8"))
        self.assertIn("约 5000 字", (evidence / "a-ship-first-output.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
