import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class SkillContractTests(unittest.TestCase):
    def test_required_package_files_exist(self):
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/information-hierarchy.md",
            "references/visual-print-contract.md",
            "references/visual-reference-workflow.md",
            "assets/layout-print.css",
            "assets/interactions.js",
            "scripts/validate_html.py",
            "scripts/validate_visual_contract.py",
            "scripts/build_reference_demo.py",
        }
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file()
        }
        self.assertLessEqual(expected, actual)

    def test_skill_routes_to_references_and_optional_capability_fragments(self):
        skill = read("SKILL.md")
        self.assertIn("references/information-hierarchy.md", skill)
        self.assertIn("references/visual-print-contract.md", skill)
        self.assertIn("references/visual-reference-workflow.md", skill)
        self.assertIn("assets/layout-print.css", skill)
        self.assertIn("assets/interactions.js", skill)
        self.assertIn("不套固定页面模板", skill)

    def test_instruction_package_is_domain_neutral(self):
        combined = "\n".join(
            read(path)
            for path in (
                "SKILL.md",
                "references/information-hierarchy.md",
                "references/visual-print-contract.md",
            )
        )
        self.assertIn("不嵌入具体领域、项目或任务类型的规则与示例", combined)
        self.assertIn("领域事实、分析方法和业务流程由调用方持有", combined)

    def test_information_hierarchy_contract_is_complete(self):
        hierarchy = read("references/information-hierarchy.md")
        for phrase in (
            "完整体系",
            "每个板块都落实主次",
            "成品只呈现主题内容本身",
            "不设置固定模块数",
            "参考文献",
        ):
            self.assertIn(phrase, hierarchy)

    def test_visual_and_delivery_contract_is_complete(self):
        combined = read("SKILL.md") + read("references/visual-print-contract.md")
        for phrase in (
            "自包含",
            "标记选中文字",
            "红色下划线",
            "A4",
            "五号",
            "横向展开",
            "真实浏览器或渲染器",
            "本次交付时间",
            "聚焦重点",
            "独立内容房间",
            "房间内部纵向滚动",
            "冷灰画布",
            "白色章节卡",
            "语义色",
            "本地编辑",
            "浮动格式工具栏",
            "不显示“AI 编辑”",
        ):
            self.assertIn(phrase, combined)

    def test_no_universal_page_limit_is_declared(self):
        combined = read("SKILL.md") + read("references/visual-print-contract.md")
        self.assertNotIn("通用页数上限", combined)
        self.assertIn("调用方可以声明最高页数", combined)

    def test_internal_depth_terms_are_not_visible_section_requirements(self):
        skill = read("SKILL.md")
        hierarchy = read("references/information-hierarchy.md")
        self.assertIn("成品不得出现", skill)
        self.assertIn("不要把内部阅读判断另做成", hierarchy)

    def test_navigation_is_room_switching_not_anchor_scroll(self):
        visual = read("references/visual-print-contract.md")
        css = read("assets/layout-print.css")
        self.assertIn("导航不是目录锚点", visual)
        self.assertIn("data-room-scroll", visual)
        self.assertIn(".room-stack", css)
        self.assertIn("overflow-y: auto", css)

    def test_editing_is_optional_local_and_exportable(self):
        skill = read("SKILL.md")
        visual = read("references/visual-print-contract.md")
        interactions = read("assets/interactions.js")
        self.assertIn("直接编辑正文", skill)
        self.assertIn("普通阅读型成品不机械加载编辑器", visual)
        self.assertIn("data-editor-toolbar", interactions)
        self.assertIn("personal-html-content", interactions)
        self.assertNotIn("AI 编辑", interactions)

    def test_capabilities_are_explicitly_independent(self):
        visual = read("references/visual-print-contract.md")
        validator = read("scripts/validate_html.py")
        self.assertIn("data-capabilities", visual)
        self.assertIn("VALID_CAPABILITIES", validator)
        self.assertIn('"navigation", "search", "focus", "review", "editor", "print"', validator)

    def test_mind_maps_and_system_emphasis_follow_confirmed_form(self):
        hierarchy = read("references/information-hierarchy.md")
        visual = read("references/visual-print-contract.md")
        self.assertIn("中心主题在左", visual)
        self.assertIn("一级分支向右", visual)
        self.assertIn("通用引导语不因版式身份而加粗或高亮", hierarchy)

    def test_knowledge_summaries_have_selective_visual_emphasis(self):
        hierarchy = read("references/information-hierarchy.md")
        visual = read("references/visual-print-contract.md")
        css = read("assets/layout-print.css")
        self.assertIn("知识总结的重点呈现", hierarchy)
        self.assertIn("必须选出最小必要内容并做静态重点呈现", hierarchy)
        self.assertIn("可以复合使用两种样式", hierarchy)
        self.assertIn("颜色必须有信息含义", visual)
        self.assertIn("粗体、文字色、淡色底、划线、色条和结论框", visual)
        self.assertIn(".system-key", css)

    def test_visual_reference_priority_and_render_gate_are_explicit(self):
        skill = read("SKILL.md")
        visual = read("references/visual-print-contract.md")
        workflow = read("references/visual-reference-workflow.md")
        css = read("assets/layout-print.css")
        for phrase in (
            "本次明确风格与参考 ＞ 用户已认可的历史视觉基线 ＞ 本 Skill 默认基线",
            "视觉参考提取与验收",
            "三层验证",
            "不得把静态校验通过称为完整视觉验收",
        ):
            self.assertIn(phrase, skill + workflow)
        self.assertIn("不能代替视觉判断", skill)
        self.assertIn("冷灰画布", visual)
        self.assertIn("蓝、绿、琥珀", visual)
        self.assertIn("personal-html-visual-baseline:v2", css)
        self.assertIn("personal-html-interactions-baseline:v2", read("assets/interactions.js"))

    def test_final_html_delivery_requires_the_domestic_publication_contract(self):
        skill = read("SKILL.md")
        self.assertIn("personal-html-publish-cn", skill)
        self.assertIn("本地交付完成", skill)
        self.assertIn("公开发布完成", skill)
        self.assertIn("HTTPS URL", skill)


if __name__ == "__main__":
    unittest.main()
