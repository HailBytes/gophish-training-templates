#!/usr/bin/env python3
"""
GoPhish Template Catalog Generator
Automatically generates CATALOG.md indexing all templates based on their metadata.json files.

Requirements:
    Python 3.6+ standard library only.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).parent.parent

SKIP_DIRS = {".git", "tools", "campaign-guides", "landing-pages", "tests", "docs"}

SPECIAL_NAMES = {
    "ai-tools": "AI Tools",
    "itsm": "ITSM",
    "latam-portuguese": "LATAM / Portuguese",
    "it-security": "IT Security",
    "e-signature": "E-Signature",
}

def format_category_name(dir_name: str) -> str:
    if dir_name in SPECIAL_NAMES:
        return SPECIAL_NAMES[dir_name]
    return dir_name.replace("-", " ").replace("_", " ").title()

def format_difficulty(diff: str) -> str:
    colors = {
        "beginner": "🟢 beginner",
        "intermediate": "🟡 intermediate",
        "advanced": "🔴 advanced",
    }
    return colors.get(diff.lower(), diff)

def format_attack_vector(av: str) -> str:
    return av.replace("_", " ").title()

def generate_catalog_markdown(categories: List[Dict[str, Any]]) -> str:
    md = []
    md.append("# GoPhish Phishing Template Catalog")
    md.append("")
    md.append("This catalog is automatically generated from template metadata. It lists all available phishing simulation templates and education pages in this repository.")
    md.append("")
    
    # Generate Table of Contents
    md.append("## Table of Contents")
    md.append("")
    for cat in categories:
        # Standard GitHub anchor logic: lowercase, spaces to hyphens, special chars removed
        anchor = cat["name"].lower().replace(" ", "-").replace("/", "")
        md.append(f"- [{cat['name']}](#{anchor})")
    md.append("")
    
    # Generate categories details
    for cat in categories:
        anchor = cat["name"].lower().replace(" ", "-").replace("/", "")
        md.append(f"## {cat['name']}")
        md.append("")
        if cat["industry"]:
            md.append(f"**Industry Focus:** {cat['industry']}  ")
        md.append(f"**Description:** {cat['description']}")
        md.append("")
        
        md.append("| Template Name | File Path | Difficulty | Attack Vector | Est. Click Rate | Education Page |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        
        for tmpl in cat["templates"]:
            tmpl_name = tmpl["name"]
            file_path = f"{cat['dir']}/{tmpl['filename']}"
            file_link = f"[{tmpl['filename']}]({file_path})"
            
            diff = format_difficulty(tmpl["difficulty"])
            av = format_attack_vector(tmpl["attack_vector"])
            click_rate = tmpl.get("estimated_click_rate", "N/A")
            
            edu_path = tmpl.get("education_page", "")
            if edu_path:
                edu_full_path = f"{cat['dir']}/{edu_path}"
                edu_link = f"[Education]({edu_full_path})"
            else:
                edu_link = "*None*"
                
            md.append(f"| {tmpl_name} | {file_link} | {diff} | {av} | {click_rate} | {edu_link} |")
        md.append("")
        
    return "\n".join(md) + "\n"

def main():
    parser = argparse.ArgumentParser(description="Generate CATALOG.md template catalog from metadata.json files")
    parser.add_argument("--check", action="store_true", help="Verify if CATALOG.md is up to date without writing")
    parser.add_argument("--dry-run", action="store_true", help="Print generated markdown instead of writing")
    args = parser.parse_args()
    
    # Find all category metadata.json files
    categories = []
    
    for path in sorted(ROOT.iterdir()):
        if not path.is_dir():
            continue
        if path.name in SKIP_DIRS:
            continue
        
        meta_file = path / "metadata.json"
        if not meta_file.exists():
            continue
            
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {meta_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        categories.append({
            "dir": path.name,
            "name": format_category_name(path.name),
            "description": data.get("description", "No description provided."),
            "industry": data.get("industry", ""),
            "templates": data.get("templates", [])
        })
        
    # Sort categories by name
    categories.sort(key=lambda x: x["name"])
    
    markdown_content = generate_catalog_markdown(categories)
    
    catalog_path = ROOT / "CATALOG.md"
    
    if args.dry_run:
        print(markdown_content)
        return
        
    if args.check:
        if not catalog_path.exists():
            print("CATALOG.md does not exist.", file=sys.stderr)
            sys.exit(1)
        existing_content = catalog_path.read_text(encoding="utf-8")
        if existing_content != markdown_content:
            print("CATALOG.md is out of date. Please run tools/generate_catalog.py to regenerate it.", file=sys.stderr)
            sys.exit(1)
        print("✓ CATALOG.md is up to date.")
        sys.exit(0)
        
    try:
        catalog_path.write_text(markdown_content, encoding="utf-8")
        print("✓ CATALOG.md generated successfully.")
    except Exception as e:
        print(f"Error writing CATALOG.md: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
