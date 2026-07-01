#!/usr/bin/env python3
"""
GoPhish Template Preview Server
Serves phishing training templates locally with GoPhish variable substitution
so contributors can visually review templates without running GoPhish.

Requirements: Python 3.6+ (no external dependencies)

Usage:
    python3 preview_server.py                       # Start server on port 8080
    python3 preview_server.py --port 9000           # Custom port
    python3 preview_server.py --host 0.0.0.0        # Listen on all interfaces
    python3 preview_server.py --name "Jane"         # Custom first name for preview
    python3 preview_server.py --email "jane@co.com" # Custom email for preview

Then open http://localhost:8080 in your browser to see the template gallery.
"""

import os
import re
import sys
import json
import argparse
import urllib.parse
from pathlib import Path
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

ROOT = Path(__file__).parent.parent

SKIP_DIRS = {".git", "tools", "campaign-guides"}
SKIP_FILES = {"education-notification.html"}

# Default preview variables
DEFAULT_VARS = {
    "FirstName": "Jane",
    "LastName": "Smith",
    "Email": "jane.smith@yourcompany.com",
    "URL": "#PHISHING_LINK_HERE",
    "Tracker": "<!-- GoPhish Tracker Pixel -->",
    "Date": datetime.now().strftime("%B %d, %Y"),
    "Position": "Software Engineer",
    "From": "IT Support <it-support@yourcompany.com>",
    "Company": "Acme Corp",
}


def safe_join(root: Path, rel_path: str) -> Optional[Path]:
    """Resolve rel_path under root, rejecting any path that escapes root
    (e.g. via `..` segments or an absolute path) to prevent directory
    traversal. Returns None if the resolved path is outside root."""
    try:
        resolved_root = root.resolve()
        candidate = (resolved_root / rel_path).resolve()
    except (OSError, ValueError):
        return None
    if candidate != resolved_root and resolved_root not in candidate.parents:
        return None
    return candidate


def substitute_gophish_vars(html: str, vars_dict: dict) -> str:
    """Replace GoPhish template variables with preview values."""
    result = html
    for key, value in vars_dict.items():
        result = result.replace(f"{{{{{'.'+key}}}}}", value)
    # Highlight any remaining unsubstituted variables
    result = re.sub(
        r'\{\{\.[A-Za-z]+\}\}',
        lambda m: f'<mark style="background:#ff6b6b;color:white;padding:2px 4px;border-radius:3px;">{m.group()}</mark>',
        result
    )
    return result


def get_all_templates(root: Path) -> list:
    """Discover all HTML templates and return sorted list of metadata."""
    templates = []
    for html_file in sorted(root.rglob("*.html")):
        parts = html_file.parts
        parts_set = set(parts)

        if SKIP_DIRS & parts_set:
            continue
        if html_file.name in SKIP_FILES:
            continue

        relative = html_file.relative_to(root)
        parts_list = list(relative.parts)
        category = parts_list[0]
        is_education = "education" in parts_set
        is_landing = "landing-pages" in parts_set

        # Load metadata if available
        metadata = {}
        metadata_path = html_file.parent / "metadata.json"
        if is_education:
            metadata_path = html_file.parent.parent / "metadata.json"

        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    meta_data = json.load(f)
                for tmpl in meta_data.get("templates", []):
                    if tmpl.get("filename") == html_file.name:
                        metadata = tmpl
                        break
            except Exception:
                pass

        templates.append({
            "path": str(relative),
            "filename": html_file.name,
            "category": category,
            "is_education": is_education,
            "is_landing": is_landing,
            "name": metadata.get("name", html_file.stem.replace("_", " ").title()),
            "difficulty": metadata.get("difficulty", ""),
            "attack_vector": metadata.get("attack_vector", ""),
            "estimated_click_rate": metadata.get("estimated_click_rate", ""),
            "tags": metadata.get("tags", []),
        })

    return templates


DIFFICULTY_COLORS = {
    "beginner": "#28a745",
    "intermediate": "#ffc107",
    "advanced": "#dc3545",
}


def render_gallery(templates: list, preview_vars: dict) -> str:
    """Render the template gallery HTML page."""
    # Group by category
    categories = {}
    for tmpl in templates:
        cat = tmpl["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tmpl)

    cards_html = ""
    for category, items in sorted(categories.items()):
        cat_display = category.replace("-", " ").title()
        cards_html += f'<div class="category-section"><h2>{cat_display}</h2><div class="card-grid">'

        for tmpl in items:
            diff_color = DIFFICULTY_COLORS.get(tmpl["difficulty"], "#6c757d")
            difficulty_badge = (
                f'<span class="badge" style="background:{diff_color}">{tmpl["difficulty"]}</span>'
                if tmpl["difficulty"] else ""
            )
            edu_badge = '<span class="badge" style="background:#6c757d">education</span>' if tmpl["is_education"] else ""
            landing_badge = '<span class="badge" style="background:#0078d4">landing page</span>' if tmpl["is_landing"] else ""

            click_rate = ""
            if tmpl["estimated_click_rate"] and not tmpl["is_education"] and not tmpl["is_landing"]:
                click_rate = f'<div class="click-rate">Est. click rate: <strong>{tmpl["estimated_click_rate"]}</strong></div>'

            encoded_path = urllib.parse.quote(tmpl["path"])
            cards_html += f'''
            <div class="card">
                <div class="card-header">
                    <div class="card-badges">{difficulty_badge}{edu_badge}{landing_badge}</div>
                    <h3>{tmpl["name"]}</h3>
                    <div class="card-meta">{tmpl["filename"]}</div>
                </div>
                <div class="card-body">
                    {click_rate}
                </div>
                <div class="card-footer">
                    <a href="/preview/{encoded_path}" target="_blank" class="btn btn-primary">Preview</a>
                    <a href="/source/{encoded_path}" target="_blank" class="btn btn-secondary">Source</a>
                </div>
            </div>'''

        cards_html += "</div></div>"

    total = len(templates)
    phishing = sum(1 for t in templates if not t["is_education"] and not t["is_landing"])
    edu = sum(1 for t in templates if t["is_education"])

    # Build preview var inputs
    var_inputs = ""
    for key, value in preview_vars.items():
        if key == "Tracker":
            continue
        var_inputs += f'''
        <div class="var-row">
            <label>{{{{{'.'+key}}}}}</label>
            <input type="text" name="{key}" value="{value}" onchange="updateVars()">
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GoPhish Template Gallery</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7f9; color: #333; }}
.header {{ background: #2d3748; color: white; padding: 20px 30px; display: flex; align-items: center; justify-content: space-between; }}
.header h1 {{ font-size: 22px; font-weight: 700; }}
.header .stats {{ font-size: 14px; color: #a0aec0; }}
.sidebar {{ position: fixed; right: 0; top: 0; width: 280px; height: 100vh; background: white; box-shadow: -2px 0 8px rgba(0,0,0,0.1); padding: 20px; overflow-y: auto; z-index: 100; }}
.sidebar h3 {{ font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #555; margin-bottom: 12px; margin-top: 20px; }}
.sidebar h3:first-child {{ margin-top: 0; }}
.var-row {{ margin-bottom: 10px; }}
.var-row label {{ display: block; font-size: 11px; font-family: monospace; color: #666; margin-bottom: 3px; }}
.var-row input {{ width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; }}
.main {{ margin-right: 280px; padding: 30px; }}
.category-section {{ margin-bottom: 40px; }}
.category-section h2 {{ font-size: 18px; font-weight: 700; color: #2d3748; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }}
.card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
.card {{ background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; }}
.card-header {{ padding: 16px 16px 8px; }}
.card-badges {{ display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }}
.badge {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 12px; color: white; text-transform: capitalize; }}
.card-header h3 {{ font-size: 15px; font-weight: 600; color: #2d3748; margin-bottom: 4px; }}
.card-meta {{ font-size: 12px; color: #888; font-family: monospace; }}
.card-body {{ padding: 8px 16px; flex: 1; }}
.click-rate {{ font-size: 13px; color: #555; }}
.card-footer {{ padding: 12px 16px; border-top: 1px solid #f0f0f0; display: flex; gap: 8px; }}
.btn {{ display: inline-block; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: 600; cursor: pointer; }}
.btn-primary {{ background: #4299e1; color: white; }}
.btn-primary:hover {{ background: #3182ce; }}
.btn-secondary {{ background: white; color: #555; border: 1px solid #ddd; }}
.btn-secondary:hover {{ background: #f7f7f7; }}
</style>
</head>
<body>
<div class="header">
    <h1>GoPhish Template Gallery</h1>
    <div class="stats">{total} total &nbsp;|&nbsp; {phishing} phishing &nbsp;|&nbsp; {edu} education</div>
</div>
<div class="sidebar">
    <h3>Preview Variables</h3>
    <p style="font-size:12px;color:#888;margin-bottom:12px;">Customize the placeholder values used in previews.</p>
    <form id="varForm">
        {var_inputs}
        <button type="button" onclick="applyVars()" class="btn btn-primary" style="width:100%;margin-top:12px;">Apply to Previews</button>
    </form>
    <h3>Legend</h3>
    <div style="font-size:13px;line-height:2;">
        <span class="badge" style="background:#28a745">beginner</span> High click rate (50-75%)<br>
        <span class="badge" style="background:#ffc107">intermediate</span> Medium (30-55%)<br>
        <span class="badge" style="background:#dc3545">advanced</span> Lower but targeted (20-45%)
    </div>
</div>
<div class="main">
    {cards_html}
</div>
<script>
function applyVars() {{
    const form = document.getElementById('varForm');
    const inputs = form.querySelectorAll('input');
    const params = new URLSearchParams();
    inputs.forEach(input => params.set(input.name, input.value));
    // Reload page with new var params would require backend support
    alert('Variable changes will apply to new previews you open.');
}}
</script>
</body>
</html>'''


class PreviewHandler(BaseHTTPRequestHandler):
    preview_vars = DEFAULT_VARS.copy()

    def log_message(self, format, *args):
        # Clean up default logging
        path = args[0].split('"')[1] if '"' in args[0] else args[0]
        print(f"  {args[1]}  {path}")

    def send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path == "/" or path == "":
            templates = get_all_templates(ROOT)
            html = render_gallery(templates, self.preview_vars)
            self.send_html(html)

        elif path.startswith("/preview/"):
            rel_path = path[len("/preview/"):]
            file_path = safe_join(ROOT, rel_path)
            if file_path is None or not file_path.exists() or not file_path.is_file():
                self.send_html("<h1>Template not found</h1>", 404)
                return
            raw_html = file_path.read_text(encoding="utf-8")
            preview_html = substitute_gophish_vars(raw_html, self.preview_vars)
            # Add a notice banner
            banner = '''<div style="position:fixed;top:0;left:0;right:0;background:#2d3748;color:white;padding:8px 16px;font-family:sans-serif;font-size:13px;z-index:9999;display:flex;justify-content:space-between;align-items:center;">
                <span>📧 Preview Mode — GoPhish variables substituted with sample data</span>
                <a href="javascript:history.back()" style="color:#63b3ed;text-decoration:none;">← Back to Gallery</a>
            </div>
            <div style="margin-top:40px;">'''
            preview_html = preview_html.replace("<body>", "<body>" + banner, 1).replace("</body>", "</div></body>", 1)
            self.send_html(preview_html)

        elif path.startswith("/source/"):
            rel_path = path[len("/source/"):]
            file_path = safe_join(ROOT, rel_path)
            if file_path is None or not file_path.exists() or not file_path.is_file():
                self.send_html("<h1>Not found</h1>", 404)
                return
            source = file_path.read_text(encoding="utf-8")
            # Escape for HTML display
            import html as html_module
            escaped = html_module.escape(source)
            html_page = f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
            <title>Source: {file_path.name}</title>
            <style>body{{font-family:monospace;background:#1e1e1e;color:#d4d4d4;padding:20px;margin:0;}}
            pre{{white-space:pre-wrap;word-break:break-word;font-size:13px;line-height:1.6;}}
            .back{{background:#2d3748;color:#63b3ed;padding:10px 16px;display:block;margin-bottom:16px;text-decoration:none;border-radius:4px;font-family:sans-serif;font-size:13px;}}</style>
            </head><body>
            <a href="javascript:history.back()" class="back">← Back</a>
            <pre>{escaped}</pre></body></html>'''
            self.send_html(html_page)

        else:
            self.send_html("<h1>404 Not Found</h1>", 404)


def main():
    parser = argparse.ArgumentParser(description="GoPhish Template Preview Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--name", default="Jane", help="Preview FirstName value")
    parser.add_argument("--last-name", default="Smith", help="Preview LastName value")
    parser.add_argument("--email", default="jane.smith@yourcompany.com", help="Preview Email value")
    args = parser.parse_args()

    PreviewHandler.preview_vars = {
        **DEFAULT_VARS,
        "FirstName": args.name,
        "LastName": args.last_name,
        "Email": args.email,
    }

    templates = get_all_templates(ROOT)
    phishing = sum(1 for t in templates if not t["is_education"] and not t["is_landing"])

    print(f"GoPhish Template Preview Server")
    print(f"Found {len(templates)} templates ({phishing} phishing templates)")
    print(f"\nOpen: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.\n")

    server = HTTPServer((args.host, args.port), PreviewHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
