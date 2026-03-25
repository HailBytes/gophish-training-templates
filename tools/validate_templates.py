#!/usr/bin/env python3
"""
GoPhish Template Validator
Validates all phishing training templates for required variables, structure, and quality.

Usage:
    python3 validate_templates.py                  # Validate all templates
    python3 validate_templates.py --dir <path>     # Validate a specific directory
    python3 validate_templates.py --file <path>    # Validate a single file
    python3 validate_templates.py --strict         # Fail on warnings too
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from html.parser import HTMLParser
from dataclasses import dataclass, field
from typing import List, Optional

ROOT = Path(__file__).parent.parent

# ── Constants ────────────────────────────────────────────────────────────────

REQUIRED_VARS = ["{{.URL}}", "{{.Tracker}}"]
RECOMMENDED_VARS = ["{{.FirstName}}", "{{.Email}}"]
OPTIONAL_VARS = ["{{.LastName}}", "{{.Date}}"]

REQUIRED_META_TAGS = ["charset", "viewport"]

EDUCATION_DIRS = ["education"]

SKIP_DIRS = {".git", "tools", "landing-pages", "campaign-guides"}
SKIP_FILES = {"credential-harvest.html", "education-notification.html"}


# ── Result dataclasses ───────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


# ── HTML structure checker ───────────────────────────────────────────────────

class HTMLStructureChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_body = False
        self.meta_tags = {}
        self.has_title = False
        self._in_title = False
        self.title_text = ""
        self.tag_stack = []

    def handle_decl(self, decl):
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()

        if tag_lower == "html":
            self.has_html = True
        elif tag_lower == "head":
            self.has_head = True
        elif tag_lower == "body":
            self.has_body = True
        elif tag_lower == "title":
            self.has_title = True
            self._in_title = True
        elif tag_lower == "meta":
            name = attrs_dict.get("name", "").lower()
            charset = attrs_dict.get("charset", "")
            if charset:
                self.meta_tags["charset"] = charset
            if name == "viewport":
                self.meta_tags["viewport"] = attrs_dict.get("content", "")

        if tag_lower not in ("br", "hr", "img", "input", "meta", "link", "area", "base"):
            self.tag_stack.append(tag_lower)

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False
        if self.tag_stack and self.tag_stack[-1] == tag.lower():
            self.tag_stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data


# ── Individual checks ────────────────────────────────────────────────────────

def check_gophish_variables(content: str, result: ValidationResult, is_education: bool):
    """Verify required and recommended GoPhish template variables."""
    if is_education:
        # Education pages don't need GoPhish variables
        return

    for var in REQUIRED_VARS:
        if var not in content:
            result.errors.append(f"Missing required GoPhish variable: {var}")

    for var in RECOMMENDED_VARS:
        if var not in content:
            result.warnings.append(f"Missing recommended GoPhish variable: {var}")

    # Check for common typos
    typos = {
        "{{.Url}}": "{{.URL}}",
        "{{.url}}": "{{.URL}}",
        "{{.tracker}}": "{{.Tracker}}",
        "{{.firstname}}": "{{.FirstName}}",
        "{{.email}}": "{{.Email}}",
    }
    for typo, correct in typos.items():
        if typo in content:
            result.errors.append(f"Typo in GoPhish variable '{typo}' — should be '{correct}'")

    # Warn about variables in href attributes that aren't using {{.URL}}
    bare_url_pattern = re.compile(r'href="http[^"]*\{\{\.', re.IGNORECASE)
    if bare_url_pattern.search(content):
        result.warnings.append("Possible misuse of {{.URL}} inside an href — ensure it's used as the complete href value")


def check_html_structure(content: str, result: ValidationResult):
    """Check basic HTML structure validity."""
    checker = HTMLStructureChecker()
    try:
        checker.feed(content)
    except Exception as e:
        result.errors.append(f"HTML parse error: {e}")
        return

    if not checker.has_doctype:
        result.warnings.append("Missing <!DOCTYPE html>")

    if not checker.has_html:
        result.errors.append("Missing <html> tag")

    if not checker.has_head:
        result.errors.append("Missing <head> tag")

    if not checker.has_body:
        result.errors.append("Missing <body> tag")

    if not checker.has_title:
        result.warnings.append("Missing <title> tag")
    elif not checker.title_text.strip():
        result.warnings.append("<title> tag is empty")

    for required in REQUIRED_META_TAGS:
        if required not in checker.meta_tags:
            if required == "viewport":
                result.errors.append("Missing <meta name='viewport'> tag — template is not mobile-responsive")
            else:
                result.warnings.append(f"Missing <meta {required}> tag")


def check_external_dependencies(content: str, result: ValidationResult, file_path: Path):
    """Check for problematic external dependencies."""
    # Bootstrap 3.x CDN is outdated
    if "bootstrap/3.3" in content or "bootstrap/3.2" in content or "bootstrap/3.1" in content:
        result.warnings.append(
            "Uses outdated Bootstrap 3.x CDN — consider migrating to inline CSS or Bootstrap 5"
        )

    # External CDN resources can break if offline
    external_cdn_pattern = re.compile(
        r'(src|href)="https?://(cdn\.|maxcdn\.|cdnjs\.|unpkg\.)', re.IGNORECASE
    )
    cdns = external_cdn_pattern.findall(content)
    if cdns:
        result.warnings.append(
            f"Found {len(cdns)} external CDN reference(s) — templates may fail without internet access"
        )


def check_education_page(template_path: Path, result: ValidationResult):
    """Check that a corresponding education page exists."""
    category_dir = template_path.parent
    education_dir = category_dir / "education"

    if not education_dir.exists():
        result.warnings.append(
            f"No education/ directory found in {category_dir.name} — consider adding educational follow-up content"
        )
        return

    edu_files = list(education_dir.glob("*.html"))
    if not edu_files:
        result.warnings.append(
            f"Education directory exists but contains no HTML files in {category_dir.name}"
        )


def check_metadata(template_path: Path, result: ValidationResult):
    """Check that metadata.json exists and references this template."""
    metadata_path = template_path.parent / "metadata.json"

    if not metadata_path.exists():
        result.warnings.append(
            "No metadata.json found in this directory — consider adding template metadata"
        )
        return

    try:
        with open(metadata_path) as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(f"metadata.json is invalid JSON: {e}")
        return

    # Check if this template is referenced in metadata
    templates = metadata.get("templates", [])
    template_filenames = [t.get("filename", "") for t in templates]

    if template_path.name not in template_filenames:
        result.warnings.append(
            f"Template '{template_path.name}' is not listed in metadata.json"
        )
        return

    # Validate metadata fields for this template
    for tmpl in templates:
        if tmpl.get("filename") == template_path.name:
            required_fields = ["name", "attack_vector", "difficulty", "gophish_variables", "suggested_subject_lines"]
            for field_name in required_fields:
                if not tmpl.get(field_name):
                    result.warnings.append(f"metadata.json missing '{field_name}' for this template")

            valid_difficulties = {"beginner", "intermediate", "advanced"}
            if tmpl.get("difficulty") not in valid_difficulties:
                result.errors.append(
                    f"Invalid difficulty '{tmpl.get('difficulty')}' — must be one of: {valid_difficulties}"
                )


def check_tracker_placement(content: str, result: ValidationResult, is_education: bool):
    """Verify {{.Tracker}} is placed correctly (outside of visible content, typically last in body)."""
    if is_education:
        return

    if "{{.Tracker}}" not in content:
        return  # Already caught by check_gophish_variables

    # Tracker should be near the end of the body, not inside visible containers
    tracker_idx = content.rfind("{{.Tracker}}")
    body_close_idx = content.lower().rfind("</body>")

    if body_close_idx != -1 and tracker_idx > body_close_idx:
        result.warnings.append("{{.Tracker}} appears after </body> — move it inside <body>")

    # Check if tracker is wrapped in a display:none or similar — acceptable
    tracker_context = content[max(0, tracker_idx - 100):tracker_idx + 50]
    if "display:none" not in tracker_context and "display: none" not in tracker_context:
        result.info.append("{{.Tracker}} is not wrapped in a hidden element — this is fine but some deployments prefer hiding it")


def check_file_size(file_path: Path, result: ValidationResult):
    """Warn if template is unusually large (may indicate embedded images bloating the file)."""
    size_kb = file_path.stat().st_size / 1024
    if size_kb > 500:
        result.warnings.append(f"Template file is {size_kb:.0f}KB — consider optimizing embedded assets")
    result.info.append(f"File size: {size_kb:.1f}KB")


# ── Main validator ───────────────────────────────────────────────────────────

def is_education_file(file_path: Path) -> bool:
    """Determine if this file is an education page (not a phishing template)."""
    return "education" in [p.name for p in file_path.parents]


def validate_file(file_path: Path) -> ValidationResult:
    result = ValidationResult(path=str(file_path.relative_to(ROOT)))

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result

    is_education = is_education_file(file_path)

    check_html_structure(content, result)
    check_gophish_variables(content, result, is_education)
    check_external_dependencies(content, result, file_path)
    check_tracker_placement(content, result, is_education)
    check_file_size(file_path, result)

    if not is_education:
        check_education_page(file_path, result)
        check_metadata(file_path, result)

    return result


def find_templates(base_dir: Path) -> List[Path]:
    """Recursively find all HTML template files, skipping excluded directories."""
    templates = []
    for path in sorted(base_dir.rglob("*.html")):
        # Skip excluded directories
        parts = set(path.parts)
        if SKIP_DIRS & parts:
            continue
        if path.name in SKIP_FILES:
            continue
        templates.append(path)
    return templates


# ── Output ───────────────────────────────────────────────────────────────────

RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"


def print_result(result: ValidationResult, verbose: bool = False):
    status = f"{GREEN}✓ PASS{RESET}" if result.passed else f"{RED}✗ FAIL{RESET}"
    warn_str = f" {YELLOW}({len(result.warnings)} warnings){RESET}" if result.warnings else ""
    print(f"  {status}{warn_str}  {DIM}{result.path}{RESET}")

    for err in result.errors:
        print(f"    {RED}ERROR{RESET}   {err}")

    for warn in result.warnings:
        print(f"    {YELLOW}WARN{RESET}    {warn}")

    if verbose:
        for info in result.info:
            print(f"    {BLUE}INFO{RESET}    {info}")


def print_summary(results: List[ValidationResult], strict: bool = False):
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    warned = sum(1 for r in results if r.has_warnings)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    print()
    print(f"{BOLD}{'─' * 60}{RESET}")
    print(f"{BOLD}Summary:{RESET} {total} templates validated")
    print(f"  {GREEN}Passed:{RESET}   {passed}")
    if failed:
        print(f"  {RED}Failed:{RESET}   {failed} ({total_errors} errors)")
    if warned:
        print(f"  {YELLOW}Warnings:{RESET} {warned} templates with {total_warnings} warnings")
    print(f"{BOLD}{'─' * 60}{RESET}")

    if strict:
        overall_pass = failed == 0 and warned == 0
    else:
        overall_pass = failed == 0

    if overall_pass:
        print(f"{GREEN}{BOLD}✓ All checks passed!{RESET}")
    else:
        print(f"{RED}{BOLD}✗ Validation failed.{RESET}")

    return overall_pass


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate GoPhish training templates")
    parser.add_argument("--dir", type=Path, default=ROOT, help="Directory to scan (default: repo root)")
    parser.add_argument("--file", type=Path, help="Validate a single file")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show informational messages")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if args.file:
        files = [args.file.resolve()]
    else:
        files = find_templates(args.dir.resolve())

    if not files:
        print(f"{YELLOW}No HTML template files found.{RESET}")
        sys.exit(0)

    print(f"{BOLD}GoPhish Template Validator{RESET}")
    print(f"Scanning {len(files)} template(s)...\n")

    results = []
    for file_path in files:
        result = validate_file(file_path)
        results.append(result)
        if not args.json:
            print_result(result, verbose=args.verbose)

    if args.json:
        output = [
            {
                "path": r.path,
                "passed": r.passed,
                "errors": r.errors,
                "warnings": r.warnings,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
        all_passed = all(r.passed for r in results)
        if args.strict:
            all_passed = all_passed and all(not r.has_warnings for r in results)
        sys.exit(0 if all_passed else 1)

    overall_pass = print_summary(results, strict=args.strict)
    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
