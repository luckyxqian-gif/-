import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_reference_demo.py"
VALIDATOR = ROOT / "scripts" / "validate_visual_contract.py"
DEMO = ROOT / "tests" / "fixtures" / "reference-driven-learning-demo.html"


class VisualContractTests(unittest.TestCase):
    def test_reference_driven_demo_keeps_the_visual_baseline(self):
        subprocess.run([sys.executable, str(BUILD)], check=True)
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(DEMO), "--profile", "reference", "--reference", "approved-reference"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"requires_render_review": true', result.stdout)

    def test_reference_profile_requires_an_identifier(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(DEMO), "--profile", "reference"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_reference", result.stdout)


if __name__ == "__main__":
    unittest.main()
