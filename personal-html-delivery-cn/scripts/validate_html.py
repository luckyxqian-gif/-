#!/usr/bin/env python3
"""Validate static, offline HTML delivery invariants."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


VALID_CAPABILITIES = {"navigation", "search", "focus", "review", "editor", "print"}
FOCUS_ACTIONS = {"focus"}
SEARCH_ACTIONS = {"search", "search-prev", "search-next", "search-close"}
REVIEW_ACTIONS = {"highlight", "remove-highlight", "save-copy"}
EDITOR_ACTIONS = {"edit", "undo", "redo", "save-copy"}
EDITOR_COMMANDS = {
    "fontSize", "bold", "italic", "underline", "strikeThrough", "foreColor",
    "createLink", "justifyLeft", "justifyCenter", "justifyRight", "removeFormat", "delete",
}
DEPENDENCY_ATTRIBUTES = {
    "script": {"src"},
    "img": {"src", "srcset"},
    "iframe": {"src"},
    "audio": {"src"},
    "video": {"src", "poster"},
    "source": {"src", "srcset"},
    "track": {"src"},
    "embed": {"src"},
    "object": {"data"},
}


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.actions: set[str] = set()
        self.classes: set[str] = set()
        self.ids: set[str] = set()
        self.navigation_targets: list[str] = []
        self.room_sections: list[str] = []
        self.tags: set[str] = set()
        self.external_dependencies: list[str] = []
        self.style_chunks: list[str] = []
        self.editor_toolbars = 0
        self.search_panels = 0
        self.search_inputs = 0
        self.search_counts = 0
        self.editor_commands: set[str] = set()
        self.capabilities: set[str] = set()
        self.editable_blocks = 0
        self.document_key = ""
        self.content_version = ""
        self._in_style = False
        self._in_section_nav = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {name.lower(): value or "" for name, value in attrs}
        self.tags.add(tag)
        if tag == "html":
            self.capabilities.update(values.get("data-capabilities", "").split())
            self.document_key = values.get("data-document-key", "")
            self.content_version = values.get("data-content-version", "")
        if values.get("data-action"):
            self.actions.add(values["data-action"])
        if "data-editor-toolbar" in values:
            self.editor_toolbars += 1
        if "data-search-panel" in values:
            self.search_panels += 1
        if "data-search-input" in values:
            self.search_inputs += 1
        if "data-search-count" in values:
            self.search_counts += 1
        if values.get("data-command"):
            self.editor_commands.add(values["data-command"])
        if "data-editable" in values:
            self.editable_blocks += 1
        self.classes.update(values.get("class", "").split())
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "nav" and "section-nav" in values.get("class", "").split():
            self._in_section_nav += 1
        if tag == "a" and self._in_section_nav and values.get("href", "").startswith("#"):
            self.navigation_targets.append(values["href"][1:])
        if "data-section" in values:
            self.room_sections.append(values.get("id", ""))
        if tag == "style":
            self._in_style = True
        if values.get("style"):
            self.style_chunks.append(values["style"])

        for attribute in DEPENDENCY_ATTRIBUTES.get(tag, set()):
            value = values.get(attribute, "")
            if value and self._is_external_asset(value):
                self.external_dependencies.append(f"{tag}[{attribute}]={value}")

        if tag == "link" and self._link_loads_asset(values):
            href = values.get("href", "")
            if href and self._is_external_asset(href):
                self.external_dependencies.append(f"link[href]={href}")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style":
            self._in_style = False
        if tag.lower() == "nav" and self._in_section_nav:
            self._in_section_nav -= 1

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.style_chunks.append(data)

    @staticmethod
    def _link_loads_asset(attrs: dict[str, str]) -> bool:
        rel = set(attrs.get("rel", "").lower().split())
        return bool(rel & {"stylesheet", "preload", "modulepreload", "icon", "manifest"})

    @staticmethod
    def _is_external_asset(value: str) -> bool:
        values = [part.strip().split()[0] for part in value.split(",") if part.strip()]
        for item in values:
            parsed = urlparse(item)
            if item.startswith(("data:", "#")):
                continue
            if parsed.scheme in {"http", "https", "ftp", "file"} or item.startswith("//"):
                return True
            if parsed.scheme not in {"", "data"}:
                return True
            if parsed.path:
                return True
        return False


def issue(code: str, message: str, **context: object) -> dict[str, object]:
    result: dict[str, object] = {"code": code, "message": message}
    if context:
        result["context"] = context
    return result


def validate(path: Path) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {
            "valid": False,
            "errors": [issue("input_error", f"Cannot read HTML: {exc}")],
            "warnings": [],
        }

    parser = ContractParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        errors.append(issue("invalid_html", f"HTML parser failed: {exc}"))

    css = "\n".join(parser.style_chunks)
    css_urls = re.findall(r"url\(\s*(['\"]?)(.*?)\1\s*\)", css, flags=re.IGNORECASE)
    css_imports = re.findall(r"@import\s+(?:url\()?\s*['\"]?([^'\"\s;)]+)", css, flags=re.IGNORECASE)
    for _, value in css_urls:
        if ContractParser._is_external_asset(value.strip()):
            parser.external_dependencies.append(f"css url={value.strip()}")
    for value in css_imports:
        if ContractParser._is_external_asset(value.strip()):
            parser.external_dependencies.append(f"css import={value.strip()}")
    if parser.external_dependencies:
        errors.append(issue(
            "external_dependency",
            "HTML loads assets that are not embedded.",
            references=sorted(set(parser.external_dependencies)),
        ))

    unknown_capabilities = sorted(parser.capabilities - VALID_CAPABILITIES)
    if unknown_capabilities:
        errors.append(issue("unknown_capability", "Unsupported delivery capabilities are declared.", capabilities=unknown_capabilities))
    if "main" not in parser.tags:
        errors.append(issue("missing_hook", "A main content region is required.", hooks=["main"]))
    if parser.capabilities & {"navigation", "search", "focus", "review", "editor"}:
        missing_identity = [name for name, value in {
            "data-document-key": parser.document_key,
            "data-content-version": parser.content_version,
        }.items() if not value]
        if missing_identity:
            errors.append(issue("missing_hook", "Interactive saved content requires a versioned document identity.", hooks=missing_identity))
    if parser.capabilities & {"focus", "review"}:
        missing_actions = sorted(FOCUS_ACTIONS - parser.actions)
        if missing_actions:
            errors.append(issue("missing_hook", "Focus delivery requires a focus control.", hooks=missing_actions))
        missing_classes = sorted(
            class_name for class_name in {"system-key"}
            if not re.search(rf"\.{re.escape(class_name)}\b", html)
        )
        if missing_classes:
            errors.append(issue("missing_hook", "Focus delivery requires system emphasis styles.", hooks=missing_classes))
        if "system-key" not in parser.classes:
            errors.append(issue(
                "missing_system_emphasis",
                "Focus delivery requires at least one real system-key node in the document body.",
            ))
    if "review" in parser.capabilities:
        missing_actions = sorted(REVIEW_ACTIONS - parser.actions)
        if missing_actions:
            errors.append(issue("missing_hook", "Review delivery requires review controls.", hooks=missing_actions))
        missing_classes = sorted(
            class_name for class_name in {"user-highlight"}
            if not re.search(rf"\.{re.escape(class_name)}\b", html)
        )
        if missing_classes:
            errors.append(issue("missing_hook", "Review delivery requires emphasis forms.", hooks=missing_classes))
    if "search" in parser.capabilities:
        missing_actions = sorted(SEARCH_ACTIONS - parser.actions)
        missing_search_hooks: list[str] = []
        if parser.search_panels != 1:
            missing_search_hooks.append("data-search-panel")
        if parser.search_inputs != 1:
            missing_search_hooks.append("data-search-input")
        if parser.search_counts != 1:
            missing_search_hooks.append("data-search-count")
        if missing_actions or missing_search_hooks:
            errors.append(issue(
                "missing_search_hook",
                "Search delivery requires a complete local search panel and controls.",
                actions=missing_actions,
                hooks=missing_search_hooks,
            ))
    if "editor" in parser.capabilities:
        missing_editor_actions = sorted(EDITOR_ACTIONS - parser.actions)
        missing_editor_hooks: list[str] = []
        if not parser.editor_toolbars:
            missing_editor_hooks.append("data-editor-toolbar")
        missing_commands = sorted(EDITOR_COMMANDS - parser.editor_commands)
        if not parser.editable_blocks:
            missing_editor_hooks.append("data-editable")
        if missing_editor_actions or missing_editor_hooks:
            errors.append(issue(
                "missing_editor_hook",
                "Editable HTML requires local editing controls and a selection toolbar.",
                actions=missing_editor_actions,
                hooks=missing_editor_hooks,
            ))
        if missing_commands:
            errors.append(issue("missing_editor_hook", "Editable HTML is missing formatting commands.", commands=missing_commands))
    interactive_capabilities = {"navigation", "search", "focus", "review", "editor"}
    if parser.capabilities & interactive_capabilities and not re.search(r"\bpersonalHtmlQa\b", html):
        errors.append(issue("missing_hook", "The observable QA hook is missing.", hooks=["personalHtmlQa"]))
    if parser.capabilities & interactive_capabilities:
        qa_assignments = len(re.findall(r"\bpersonalHtmlQa\s*=", html))
        if qa_assignments != 1:
            errors.append(issue(
                "duplicate_interaction_controller",
                "Interactive delivery must expose exactly one active QA controller.",
                count=qa_assignments,
            ))
        if "personal-html-interactions-baseline:v2" not in html:
            errors.append(issue(
                "missing_interaction_baseline",
                "Interactive delivery must inline the verified interactions.js baseline instead of a simplified replacement.",
            ))
    if "navigation" in parser.capabilities:
        if "section-nav" not in parser.classes or "room-stack" not in parser.classes:
            errors.append(issue("missing_navigation_hook", "Navigation delivery requires section navigation and a room stack."))
        if not parser.navigation_targets:
            errors.append(issue("missing_navigation_hook", "Navigation delivery requires section targets."))
        missing_targets = sorted(set(parser.navigation_targets) - parser.ids)
        if missing_targets:
            errors.append(issue(
                "broken_navigation",
                "Section navigation links must target elements in the same document.",
                targets=missing_targets,
            ))
        nav_duplicates = sorted(target for target in set(parser.navigation_targets) if parser.navigation_targets.count(target) != 1)
        room_duplicates = sorted(section for section in set(parser.room_sections) if parser.room_sections.count(section) != 1)
        missing_room_ids = parser.room_sections.count("")
        room_targets = set(parser.room_sections) - {""}
        entries_without_room = sorted(set(parser.navigation_targets) - room_targets)
        rooms_without_entry = sorted(room_targets - set(parser.navigation_targets))
        if nav_duplicates or room_duplicates or missing_room_ids or entries_without_room or rooms_without_entry:
            errors.append(issue(
                "invalid_room_mapping",
                "Navigation requires a one-to-one mapping between page-top entries and content rooms.",
                duplicate_entries=nav_duplicates,
                duplicate_rooms=room_duplicates,
                rooms_without_ids=missing_room_ids,
                entries_without_room=entries_without_room,
                rooms_without_entry=rooms_without_entry,
            ))

    media_headers = re.findall(r"@media\s+([^\{]+)\{", html, flags=re.IGNORECASE)
    bad_mobile_headers = [
        header.strip()
        for header in media_headers
        if "max-width" in header.lower() and not re.search(r"\bscreen\b", header, flags=re.IGNORECASE)
    ]
    if bad_mobile_headers:
        errors.append(issue(
            "unqualified_mobile_media",
            "Mobile max-width media queries must be screen-qualified.",
            queries=bad_mobile_headers,
        ))

    if "print" in parser.capabilities:
        print_contract_missing: list[str] = []
        if not re.search(r"@page\s*\{", html, flags=re.IGNORECASE):
            print_contract_missing.append("@page")
        if not re.search(r"\bbreak-inside\s*:\s*avoid", html, flags=re.IGNORECASE):
            print_contract_missing.append("break-inside: avoid")
        print_blocks = re.findall(r"@media\s+print\s*\{(.*?)\n\s*\}", html, flags=re.IGNORECASE | re.DOTALL)
        print_css = "\n".join(print_blocks)
        def hidden(selector: str) -> bool:
            return bool(re.search(re.escape(selector) + r"[^\{]*\{[^\}]*display\s*:\s*none", print_css, flags=re.IGNORECASE | re.DOTALL))
        if parser.actions and not (hidden(".toolbar") or hidden("[data-action")):
            print_contract_missing.append("print-control hiding")
        if "navigation" in parser.capabilities and not hidden(".section-nav"):
            print_contract_missing.append("navigation hiding")
        if "editor" in parser.capabilities and not hidden(".selection-toolbar"):
            print_contract_missing.append("editor hiding")
        if print_contract_missing:
            errors.append(issue(
                "missing_print_contract",
                "Print layout contract is incomplete.",
                requirements=print_contract_missing,
            ))

    if "<!doctype html>" not in html.lower():
        warnings.append(issue("missing_doctype", "Use an HTML5 doctype for predictable rendering."))

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        result = {
            "valid": False,
            "errors": [issue("usage_error", "Usage: validate_html.py PATH")],
            "warnings": [],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    result = validate(Path(argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
