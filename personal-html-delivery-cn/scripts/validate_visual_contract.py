#!/usr/bin/env python3
"""Check observable visual-baseline hooks; this never substitutes for rendered review."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class VisualParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.classes: set[str] = set()
        self.tags: set[str] = set()
        self.capabilities: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        self.tags.add(tag.lower())
        self.classes.update(values.get("class", "").split())
        if tag.lower() == "html":
            self.capabilities.update(values.get("data-capabilities", "").split())


def result_issue(code: str, message: str, **context: object) -> dict[str, object]:
    issue: dict[str, object] = {"code": code, "message": message}
    if context:
        issue["context"] = context
    return issue


def validate(path: Path, profile: str, reference: str | None) -> dict[str, object]:
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {"valid": False, "errors": [result_issue("input_error", str(exc))], "warnings": [], "requires_render_review": True}

    parser = VisualParser()
    parser.feed(html)
    parser.close()
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if profile in {"baseline", "reference"}:
        if "personal-html-visual-baseline:v2" not in html:
            errors.append(result_issue("missing_visual_baseline", "The approved visual baseline was not inlined."))
        missing_classes = sorted({"document-header", "document-section"} - parser.classes)
        if missing_classes:
            errors.append(result_issue("missing_visual_hierarchy", "The high-density visual hierarchy is incomplete.", classes=missing_classes))
        if not ({"system-key", "key-phrase"} & parser.classes):
            errors.append(result_issue("missing_visual_emphasis", "The document has no explicit system emphasis node."))
    if profile == "reference" and not reference:
        errors.append(result_issue("missing_reference", "Reference-driven review needs the reference identifier or path."))
    if profile == "custom":
        warnings.append(result_issue("custom_profile", "Custom visual profiles need a manual comparison against the user's stated design constraints."))

    if not re.search(r"@media\s+(?:screen\s+and\s+)?\(max-width", html, flags=re.IGNORECASE):
        warnings.append(result_issue("missing_narrow_screen_rule", "No narrow-screen rule was found; inspect the result manually."))
    if "print" in parser.capabilities and not re.search(r"@media\s+print", html, flags=re.IGNORECASE):
        errors.append(result_issue("missing_print_style", "Print is declared but no print style was found."))

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "profile": profile,
        "reference": reference,
        "requires_render_review": True,
        "render_review": ["desktop", "narrow-screen", "print", "declared-interactions"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--profile", choices=("reference", "baseline", "custom"), required=True)
    parser.add_argument("--reference", help="Reference path or URL for a reference-driven review")
    args = parser.parse_args()
    output = validate(args.html, args.profile, args.reference)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
