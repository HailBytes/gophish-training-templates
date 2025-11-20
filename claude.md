# Claude Code Quick Reference

## Project Overview

GoPhish Training Templates - Professional phishing simulation templates for security awareness training.

## Quick Commands

### Search and Analysis

Find all templates with emojis:
```bash
grep -r "🎯\|🔒\|⚠️\|📧\|💰\|🎵\|☕\|🏛️\|📰\|🚨" --include="*.html" .
```

List all email templates:
```bash
find . -name "*.html" -not -path "*/education/*" -not -path "*/landing-pages/*" | sort
```

List all landing pages:
```bash
find ./landing-pages -name "*.html"
```

Count templates by category:
```bash
for dir in */; do echo "$dir: $(find "$dir" -maxdepth 1 -name "*.html" | wc -l)"; done
```

### Template Management

Check for GoPhish variables:
```bash
grep -r "{{\.FirstName}}\|{{\.Email}}\|{{\.URL}}\|{{\.Tracker}}" --include="*.html"
```

Find templates using specific variables:
```bash
grep -l "{{\.LastName}}" **/*.html
```

Validate HTML files:
```bash
find . -name "*.html" -exec echo "Checking: {}" \; -exec head -1 {} \;
```

### Testing and Validation

Check for broken inline styles:
```bash
grep -n "style=" **/*.html | grep -v "style=\""
```

Find deprecated Bootstrap CDN links:
```bash
grep -r "bootstrap.*3\.3\.7" --include="*.html"
```

Check mobile viewport tags:
```bash
grep -L "viewport" **/*.html
```

### Documentation

List all markdown files:
```bash
find . -name "*.md" | sort
```

Word count for documentation:
```bash
wc -w campaign-guides/*.md
```

### Template Categories

Current template structure:
- delivery-shipping/ - Package delivery themed templates
- it-security/ - IT security alerts and system updates
- cloud-services/ - Cloud platform phishing (Dropbox, Google Drive)
- social-media/ - Social media platform impersonations
- financial/ - Banking and payment themed templates
- entertainment/ - Entertainment service phishing
- corporate/ - Corporate communications and news
- government/ - Government agency impersonations
- microsoft/ - Microsoft service themed templates
- landing-pages/ - Credential harvest and education pages

### Development Workflow

Create new template:
```bash
# Copy from existing template structure
cp it-security/email_issues.html new-category/new_template.html
```

Test GoPhish variable rendering:
```bash
# Variables to test: {{.FirstName}}, {{.LastName}}, {{.Email}}, {{.URL}}, {{.Tracker}}
```

### Quality Checks

Templates should:
- Use realistic, professional language
- Avoid excessive emojis or "cartoony" elements
- Include proper GoPhish tracking variables
- Be mobile responsive
- Follow real-world phishing patterns
- Match legitimate service styling

## Template Design Principles

1. **Realism**: Templates should closely mimic actual corporate/service emails
2. **Professionalism**: Avoid emojis, excessive styling, or unrealistic language
3. **Effectiveness**: Use proven social engineering techniques
4. **Education**: Each template should have corresponding educational content
5. **Ethics**: Designed for authorized security awareness training only

## Common GoPhish Variables

- `{{.FirstName}}` - Recipient's first name
- `{{.LastName}}` - Recipient's last name
- `{{.Email}}` - Recipient's email address
- `{{.URL}}` - Unique tracking URL for the campaign
- `{{.Tracker}}` - Invisible tracking pixel
- `{{.From}}` - Sender email address
- `{{.RId}}` - Recipient ID

## License

Mozilla Public License 2.0 (MPL-2.0)
