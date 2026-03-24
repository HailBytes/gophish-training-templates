#!/usr/bin/env python3
"""
GoPhish Template Importer
Bulk-imports phishing email templates and landing pages into GoPhish via its REST API.

Requirements:
    pip install requests

Usage:
    # Import all templates
    python3 import_to_gophish.py --url https://gophish.yourcompany.com:3333 --api-key YOUR_API_KEY

    # Import a specific category
    python3 import_to_gophish.py --url https://... --api-key ... --category it-security

    # Import a single file
    python3 import_to_gophish.py --url https://... --api-key ... --file path/to/template.html

    # Dry run (show what would be imported without making API calls)
    python3 import_to_gophish.py --url https://... --api-key ... --dry-run

    # Import landing pages too
    python3 import_to_gophish.py --url https://... --api-key ... --include-landing-pages

    # Skip TLS verification (self-signed certs are common with GoPhish)
    python3 import_to_gophish.py --url https://... --api-key ... --no-verify-tls
"""

import os
import re
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

ROOT = Path(__file__).parent.parent

SKIP_DIRS = {".git", "tools", "campaign-guides"}
SKIP_FILES = {"education-notification.html"}
EDUCATION_DIRS = {"education"}


# ── GoPhish API client ───────────────────────────────────────────────────────

class GoPhishClient:
    def __init__(self, base_url: str, api_key: str, verify_tls: bool = True):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_tls = verify_tls

        # Patch SSL context for self-signed certs if needed
        if not verify_tls:
            import ssl
            self._ssl_ctx = ssl.create_default_context()
            self._ssl_ctx.check_hostname = False
            self._ssl_ctx.verify_mode = ssl.CERT_NONE
        else:
            self._ssl_ctx = None

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Any]:
        url = f"{self.base_url}/api/{endpoint}/?api_key={self.api_key}"
        body = json.dumps(data).encode("utf-8") if data else None
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            if self._ssl_ctx:
                import ssl
                with urllib.request.urlopen(req, context=self._ssl_ctx) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            else:
                with urllib.request.urlopen(req) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, {"error": body}
        except Exception as e:
            return 0, {"error": str(e)}

    def get_templates(self) -> List[Dict]:
        status, data = self._request("GET", "templates")
        if status != 200:
            raise RuntimeError(f"Failed to fetch templates: {data}")
        return data or []

    def create_template(self, name: str, html: str, text: str = "", subject: str = "") -> Tuple[bool, str]:
        payload = {
            "name": name,
            "subject": subject or f"[Training] {name}",
            "html": html,
            "text": text,
        }
        status, data = self._request("POST", "templates", payload)
        if status == 201:
            return True, f"Created template ID {data.get('id', '?')}"
        elif status == 409:
            return False, "Template with this name already exists (skipped)"
        else:
            return False, f"API error {status}: {data.get('message', data.get('error', str(data)))}"

    def get_pages(self) -> List[Dict]:
        status, data = self._request("GET", "pages")
        if status != 200:
            raise RuntimeError(f"Failed to fetch pages: {data}")
        return data or []

    def create_page(self, name: str, html: str, capture_credentials: bool = False,
                    capture_passwords: bool = False, redirect_url: str = "") -> Tuple[bool, str]:
        payload = {
            "name": name,
            "html": html,
            "capture_credentials": capture_credentials,
            "capture_passwords": capture_passwords,
            "redirect_url": redirect_url,
        }
        status, data = self._request("POST", "pages", payload)
        if status == 201:
            return True, f"Created landing page ID {data.get('id', '?')}"
        elif status == 409:
            return False, "Landing page with this name already exists (skipped)"
        else:
            return False, f"API error {status}: {data.get('message', data.get('error', str(data)))}"

    def health_check(self) -> bool:
        try:
            status, _ = self._request("GET", "templates")
            return status in (200, 404)
        except Exception:
            return False


# ── Template discovery ───────────────────────────────────────────────────────

def is_education_file(path: Path) -> bool:
    return any(part in EDUCATION_DIRS for part in path.parts)


def is_landing_page(path: Path) -> bool:
    return "landing-pages" in path.parts


def discover_templates(root: Path, category: Optional[str] = None) -> List[Path]:
    """Find phishing templates (not education pages, not landing pages)."""
    results = []
    for html_file in sorted(root.rglob("*.html")):
        parts_set = set(html_file.parts)
        if SKIP_DIRS & parts_set:
            continue
        if html_file.name in SKIP_FILES:
            continue
        if is_education_file(html_file):
            continue
        if is_landing_page(html_file):
            continue

        if category:
            # Check if this file is in the specified category directory
            relative = html_file.relative_to(root)
            if str(relative.parts[0]) != category:
                continue

        results.append(html_file)
    return results


def discover_landing_pages(root: Path) -> List[Path]:
    """Find landing page templates."""
    landing_dir = root / "landing-pages"
    if not landing_dir.exists():
        return []
    return sorted(landing_dir.glob("*.html"))


def make_template_name(file_path: Path, root: Path) -> str:
    """Generate a descriptive template name from the file path."""
    relative = file_path.relative_to(root)
    parts = list(relative.parts)
    # e.g., "it-security/email_issues.html" → "IT Security — Email Issues"
    category = parts[0].replace("-", " ").title()
    stem = parts[-1].replace(".html", "").replace("_", " ").title()
    return f"{category} — {stem}"


def load_metadata_subject(file_path: Path) -> Optional[str]:
    """Load a suggested subject line from metadata.json if available."""
    metadata_path = file_path.parent / "metadata.json"
    if not metadata_path.exists():
        return None
    try:
        with open(metadata_path) as f:
            metadata = json.load(f)
        for tmpl in metadata.get("templates", []):
            if tmpl.get("filename") == file_path.name:
                subjects = tmpl.get("suggested_subject_lines", [])
                if subjects:
                    return subjects[0]
    except Exception:
        pass
    return None


# ── Import logic ─────────────────────────────────────────────────────────────

def process_html_for_gophish(html: str) -> str:
    """
    Ensure HTML is suitable for GoPhish import.
    GoPhish expects the raw HTML with {{.Variable}} placeholders intact.
    """
    return html.strip()


# ── CLI ──────────────────────────────────────────────────────────────────────

RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BOLD = "\033[1m"
DIM = "\033[2m"


def main():
    parser = argparse.ArgumentParser(
        description="Bulk-import GoPhish training templates via the GoPhish API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--url", required=True, help="GoPhish base URL (e.g. https://localhost:3333)")
    parser.add_argument("--api-key", required=True, help="GoPhish API key")
    parser.add_argument("--category", help="Only import templates from this category directory")
    parser.add_argument("--file", type=Path, help="Import a single template file")
    parser.add_argument("--include-landing-pages", action="store_true",
                        help="Also import landing pages from landing-pages/")
    parser.add_argument("--no-verify-tls", action="store_true",
                        help="Disable TLS certificate verification (for self-signed certs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be imported without making API calls")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Seconds between API calls to avoid rate limiting (default: 0.5)")
    args = parser.parse_args()

    client = GoPhishClient(
        base_url=args.url,
        api_key=args.api_key,
        verify_tls=not args.no_verify_tls,
    )

    print(f"{BOLD}GoPhish Template Importer{RESET}")
    print(f"Target: {args.url}")

    if not args.dry_run:
        print("Checking GoPhish connectivity...")
        if not client.health_check():
            print(f"{RED}ERROR: Cannot connect to GoPhish at {args.url}{RESET}")
            print("Check your URL, API key, and that GoPhish is running.")
            sys.exit(1)
        print(f"{GREEN}✓ Connected successfully{RESET}\n")
    else:
        print(f"{YELLOW}DRY RUN MODE — no API calls will be made{RESET}\n")

    # Discover templates
    if args.file:
        template_files = [args.file.resolve()]
    else:
        template_files = discover_templates(ROOT, category=args.category)

    landing_pages = []
    if args.include_landing_pages and not args.file:
        landing_pages = discover_landing_pages(ROOT)

    total = len(template_files) + len(landing_pages)
    if total == 0:
        print(f"{YELLOW}No templates found to import.{RESET}")
        sys.exit(0)

    print(f"Found {len(template_files)} email template(s)" +
          (f" + {len(landing_pages)} landing page(s)" if landing_pages else "") + "\n")

    # Import email templates
    success_count = 0
    skip_count = 0
    error_count = 0

    if template_files:
        print(f"{BOLD}Email Templates:{RESET}")

    for file_path in template_files:
        name = make_template_name(file_path, ROOT)
        subject = load_metadata_subject(file_path) or ""

        html = file_path.read_text(encoding="utf-8")
        html = process_html_for_gophish(html)

        if args.dry_run:
            print(f"  {DIM}[dry-run]{RESET} Would import: {BOLD}{name}{RESET}")
            if subject:
                print(f"    Subject: {subject}")
            success_count += 1
            continue

        ok, msg = client.create_template(name=name, html=html, subject=subject)
        if ok:
            print(f"  {GREEN}✓{RESET} {name}")
            success_count += 1
        elif "already exists" in msg:
            print(f"  {YELLOW}→{RESET} {name} — {msg}")
            skip_count += 1
        else:
            print(f"  {RED}✗{RESET} {name} — {msg}")
            error_count += 1

        if args.delay > 0:
            time.sleep(args.delay)

    # Import landing pages
    if landing_pages:
        print(f"\n{BOLD}Landing Pages:{RESET}")
        for file_path in landing_pages:
            name = f"Landing Page — {file_path.stem.replace('_', ' ').replace('-', ' ').title()}"
            html = file_path.read_text(encoding="utf-8")
            is_harvest = "credential" in file_path.name.lower() or "harvest" in file_path.name.lower()

            if args.dry_run:
                print(f"  {DIM}[dry-run]{RESET} Would import: {BOLD}{name}{RESET}"
                      + (" (credential capture enabled)" if is_harvest else ""))
                success_count += 1
                continue

            ok, msg = client.create_page(
                name=name,
                html=html,
                capture_credentials=is_harvest,
                capture_passwords=False,  # Never capture passwords in training
            )
            if ok:
                print(f"  {GREEN}✓{RESET} {name}")
                success_count += 1
            elif "already exists" in msg:
                print(f"  {YELLOW}→{RESET} {name} — {msg}")
                skip_count += 1
            else:
                print(f"  {RED}✗{RESET} {name} — {msg}")
                error_count += 1

            if args.delay > 0:
                time.sleep(args.delay)

    # Summary
    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{'[dry-run] ' if args.dry_run else ''}Results: "
          f"{GREEN}{success_count} imported{RESET}"
          + (f", {YELLOW}{skip_count} skipped{RESET}" if skip_count else "")
          + (f", {RED}{error_count} failed{RESET}" if error_count else ""))

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
