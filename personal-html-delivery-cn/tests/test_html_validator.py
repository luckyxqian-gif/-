import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_html.py"
BUILD_DEMO = ROOT / "scripts" / "build_reference_demo.py"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


class HtmlValidatorTests(unittest.TestCase):
    def test_static_delivery_needs_no_optional_controls(self):
        result = run(ROOT / "tests" / "fixtures" / "valid-static.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_delivery_fixture_passes_static_validation(self):
        result = run(ROOT / "tests" / "fixtures" / "valid-delivery.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_external_dependency_fails(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-external.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("external_dependency", result.stdout)

    def test_missing_interaction_hooks_fail(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-missing-controls.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_hook", result.stdout)

    def test_review_requires_a_real_system_emphasis_node(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-no-system-emphasis.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_system_emphasis", result.stdout)

    def test_broken_section_navigation_fails(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-broken-navigation.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken_navigation", result.stdout)

    def test_navigation_requires_one_entry_per_room(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-room-mapping.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid_room_mapping", result.stdout)

    def test_edit_mode_without_selection_toolbar_fails(self):
        result = run(ROOT / "tests" / "fixtures" / "invalid-missing-editor.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_editor_hook", result.stdout)

    def test_reference_driven_demo_passes_full_static_contract(self):
        subprocess.run([sys.executable, str(BUILD_DEMO)], check=True)
        result = run(ROOT / "tests" / "fixtures" / "reference-driven-learning-demo.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
