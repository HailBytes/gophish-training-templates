# Contributing to GoPhish Training Templates

Thank you for helping improve security awareness training for the community! This guide covers everything you need to know to contribute a new template, fix a bug, or improve existing content.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What We're Looking For](#what-were-looking-for)
- [Quick Start](#quick-start)
- [Template Structure](#template-structure)
- [Naming Conventions](#naming-conventions)
- [Template Scaffold](#template-scaffold)
- [Education Page Scaffold](#education-page-scaffold)
- [Metadata Scaffold](#metadata-scaffold)
- [Submission Checklist](#submission-checklist)
- [Running the Validator](#running-the-validator)
- [Preview Your Template](#preview-your-template)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

These templates are for **authorized security awareness training only**. By contributing, you agree that your contributions:

- Are intended for defensive, educational purposes
- Do not include actual malware, exploit code, or credential-stealing payloads
- Will not be used to target individuals without their organization's authorization
- Follow responsible disclosure principles

**We will reject contributions** that appear designed for malicious use.

---

## What We're Looking For

We especially welcome contributions of:

- **New attack vectors** not yet covered (current gaps: vishing scripts, newer SaaS platforms, AI-themed lures)
- **Industry-specific variations** of existing templates (e.g., a healthcare-specific Okta template)
- **Non-English templates** for international organizations (Spanish, French, German, Japanese, etc.)
- **Improved education pages** with better knowledge checks or more current threat context
- **Bug fixes** for templates that aren't rendering correctly on mobile or in GoPhish
- **Metadata improvements** for templates missing difficulty ratings or subject lines

---

## Quick Start

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/gophish-training-templates.git
cd gophish-training-templates

# 2. Create a feature branch
git checkout -b add-my-new-template

# 3. Create your template files (see structure below)

# 4. Validate your template
python3 tools/validate_templates.py --file path/to/your/template.html

# 5. Preview it in the browser
python3 tools/preview_server.py
# Open http://localhost:8080

# 6. Commit and push
git add .
git commit -m "feat: add [Platform] [scenario] template"
git push origin add-my-new-template

# 7. Open a Pull Request on GitHub
```

---

## Template Structure

Each category lives in its own directory. The expected structure is:

```
category-name/
├── template_name.html          # Phishing template
├── another_template.html       # Optional additional template
├── metadata.json               # Template metadata (see below)
└── education/
    └── category_education.html # Education page shown after click
```

**Existing categories:**
`cloud-services` · `collaboration` · `corporate` · `delivery-shipping` · `e-signature` · `education` · `entertainment` · `financial` · `government` · `healthcare` · `hospitality` · `hr-payroll` · `identity` · `it-security` · `itsm` · `legal` · `manufacturing` · `microsoft` · `quishing` · `retail` · `smishing` · `social-media` · `technology` · `utilities`

If your template fits an existing category, add it there. For genuinely new categories, create a new directory following the naming convention (lowercase, hyphen-separated).

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Directory | lowercase, hyphenated | `cloud-services` |
| Template file | snake_case, descriptive | `dropbox_storage_full.html` |
| Education file | `{category}_education.html` | `cloud_services_education.html` |
| Metadata file | `metadata.json` | `metadata.json` |
| Template `name` in metadata | Title Case with dash | `Dropbox — Storage Full Warning` |

---

## Template Scaffold

Copy this scaffold for new phishing email templates:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><!-- Descriptive title matching the scenario --></title>
    <style>
        /* Self-contained CSS — avoid external CDN dependencies */
        body {
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0,0,0,0.12);
        }
        /* ... rest of your CSS ... */
    </style>
</head>
<body>
    <div class="container">
        <!-- Header matching the impersonated platform/brand -->
        <div class="header">
            <!-- Brand name or logo approximation using CSS/SVG -->
        </div>

        <div class="content">
            <!-- Use {{.FirstName}} for personalization -->
            <p>Dear {{.FirstName}},</p>

            <!-- Template body: your phishing scenario -->
            <!-- Keep the scenario realistic but not so convincing it causes real harm -->

            <!-- Primary CTA — must use {{.URL}} for GoPhish tracking -->
            <p style="text-align: center; margin: 28px 0;">
                <a href="{{.URL}}" class="cta-button">Action Button Text</a>
            </p>

            <!-- Footer / unsubscribe text matching the impersonated brand -->
            <p style="font-size: 12px; color: #888;">
                This email was sent to {{.Email}}.
            </p>
        </div>
    </div>

    <!-- GoPhish tracking pixel — required, place just before </body> -->
    {{.Tracker}}
</body>
</html>
```

### Required GoPhish Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `{{.URL}}` | **Yes** | Must be in at least one clickable link |
| `{{.Tracker}}` | **Yes** | Invisible tracking pixel — place before `</body>` |
| `{{.FirstName}}` | Recommended | Personalization; use if it makes sense for the scenario |
| `{{.Email}}` | Recommended | Recipient email; helps with realism |
| `{{.LastName}}` | Optional | Full name contexts (legal docs, HR) |
| `{{.Date}}` | Optional | Current date for time-sensitive scenarios |

### Design Guidelines

- **Mobile-first:** Test that `max-width: 600px` renders well on a phone screen
- **Self-contained CSS:** Avoid external CDN links — they may be blocked by email clients and corporate proxies
- **Brand approximation:** Use CSS color values and text to approximate brand styling — don't use scraped logos or copyrighted assets
- **Realistic but not weaponized:** Scenarios should be convincing enough to train employees but not so polished they'd fool a security professional
- **No actual malware:** The only payload should be `{{.URL}}` pointing to GoPhish's landing page

---

## Education Page Scaffold

Every phishing template should have a corresponding education page. If your category already has one, check if your template scenario is covered. If not, create one or update the existing page.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Awareness: [Category] Phishing</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .alert-danger { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .technique-box { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }
        .protection-box { background: #d1ecf1; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #17a2b8; }
        h1 { color: #dc3545; }
        h2 { color: #495057; border-bottom: 2px solid #dc3545; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="text-align:center; margin-bottom:40px;">
            <h1>🚨 [Category] Phishing Detected!</h1>
            <div class="alert-danger">
                <strong>⚠️ You clicked on a simulated [scenario] phishing email.</strong><br>
                This was a training exercise — let's learn how to spot these attacks.
            </div>
        </div>

        <section>
            <h2>Why [Category] Attacks Are Effective</h2>
            <!-- 3-5 bullet points explaining the psychology/mechanics -->
        </section>

        <section>
            <h2>🎭 Common Attack Patterns</h2>
            <div class="technique-box">
                <ul>
                    <!-- Specific tactics used in this template category -->
                </ul>
            </div>
        </section>

        <section>
            <h2>🚩 Red Flags to Watch For</h2>
            <div class="alert-danger">
                <ul>
                    <!-- Specific red flags visible in this category's templates -->
                </ul>
            </div>
        </section>

        <section>
            <h2>✅ How to Stay Safe</h2>
            <div class="protection-box">
                <ol>
                    <!-- Actionable protective steps -->
                </ol>
            </div>
        </section>

        <section>
            <h2>🧠 Knowledge Check</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Scenario question testing the key lesson from this template?</strong></p>
                <div style="margin: 15px 0;">
                    <input type="radio" id="q1a" name="q1" value="a">
                    <label for="q1a">Wrong answer (tempting but incorrect)</label><br>
                    <input type="radio" id="q1b" name="q1" value="b">
                    <label for="q1b">Correct answer (verify via official channel)</label><br>
                    <input type="radio" id="q1c" name="q1" value="c">
                    <label for="q1c">Wrong answer</label><br>
                    <input type="radio" id="q1d" name="q1" value="d">
                    <label for="q1d">Wrong answer (passive avoidance)</label>
                </div>
                <details style="margin-top: 20px;">
                    <summary style="cursor: pointer; color: #007bff;"><strong>Click for Answer</strong></summary>
                    <div style="background: #d4edda; padding: 15px; margin-top: 10px; border-radius: 5px;">
                        <p><strong>Correct Answer: B</strong> — Explanation of why B is correct and the key takeaway.</p>
                    </div>
                </details>
            </div>
        </section>

        <section style="text-align: center; margin-top: 40px; padding: 20px; background: linear-gradient(135deg, #YOUR_COLOR 0%, #DARKER_COLOR 100%); color: white; border-radius: 8px;">
            <h2>🎓 Training Complete!</h2>
            <p>One-sentence takeaway from this training module.</p>
            <p><strong>Questions?</strong> Contact IT Security at security@company.com</p>
        </section>
    </div>
</body>
</html>
```

---

## Metadata Scaffold

Every category directory must contain a `metadata.json`. Add your template to the `templates` array:

```json
{
  "category": "your-category",
  "industry": "Cross-industry",
  "description": "Brief description of this category's phishing angle",
  "templates": [
    {
      "filename": "your_template.html",
      "name": "Human Readable Template Name",
      "attack_vector": "credential_harvest",
      "difficulty": "intermediate",
      "estimated_click_rate": "35-55%",
      "gophish_variables": ["{{.FirstName}}", "{{.Email}}", "{{.URL}}", "{{.Tracker}}"],
      "suggested_subject_lines": [
        "Primary subject line (most effective)",
        "Alternative subject line B",
        "Alternative subject line C"
      ],
      "education_page": "education/your_category_education.html",
      "tags": ["tag1", "tag2", "platform-name", "attack-type"],
      "notes": "Optional: deployment tips, target audience, timing recommendations"
    }
  ],
  "gophish_version_tested": "0.12.1",
  "last_updated": "2024-01-01"
}
```

### Metadata schema (enforced by the validator)

The validator checks the shape of every `metadata.json`. The following are **errors** (CI-blocking):

| Field | Rule |
|---|---|
| `filename` | Required; must match an existing file in the directory |
| `name` | Required, non-empty |
| `attack_vector` | Required; one of `credential_harvest` · `malware_delivery` · `information_gathering` · `awareness_only` |
| `difficulty` | Required; one of `beginner` · `intermediate` · `advanced` |
| `estimated_click_rate` | Required; a percentage range like `40-60%` (regex `^\d{1,3}-\d{1,3}%$`) |
| `gophish_variables` | Required list; must include `{{.URL}}` and `{{.Tracker}}` |
| `suggested_subject_lines` | Required; non-empty list |
| `education_page` | Required, non-empty |
| `tags` | Required; non-empty list |
| `templates` (top level) | Required; non-empty list, no duplicate `filename`s |

The following are **warnings** (non-blocking, but please fix):

- `notes` — recommended deployment guidance for operators
- top-level `description`, `gophish_version_tested`, `last_updated` (ISO `YYYY-MM-DD`)
- `category` should match the directory name

> All templates are also compatible with **[HailBytes SAT](https://hailbytes.com/sat)**, the
> enterprise-ready successor to GoPhish, which imports this metadata directly.

---

## Submission Checklist

Before opening a pull request, verify all items:

### Template File
- [ ] `<!DOCTYPE html>` present
- [ ] `<meta charset="UTF-8">` present
- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1.0">` present (mobile responsive)
- [ ] `{{.URL}}` used in at least one link
- [ ] `{{.Tracker}}` present before `</body>`
- [ ] `{{.FirstName}}` used for personalization (if appropriate)
- [ ] No external CDN dependencies (Bootstrap CDN, etc.) — use inline CSS
- [ ] No actual malware, credentials, or exploit code
- [ ] Renders correctly at 600px width (email standard)
- [ ] File size under 200KB

### Education Page
- [ ] Exists in `education/` subdirectory of the category
- [ ] Covers the specific attack vector used in the template
- [ ] Includes at least 3 red flags to watch for
- [ ] Includes at least 3 protective actions
- [ ] Includes a knowledge check question with revealed answer
- [ ] Mobile viewport meta tag present

### Metadata
- [ ] `metadata.json` exists in the category directory
- [ ] Template is listed in the `templates` array
- [ ] `filename` matches the actual file name
- [ ] `attack_vector` is one of: `credential_harvest`, `malware_delivery`, `information_gathering`, `awareness_only`
- [ ] `difficulty` is one of: `beginner`, `intermediate`, `advanced`
- [ ] `estimated_click_rate` is a range like `40-60%`
- [ ] At least 2 `suggested_subject_lines` provided
- [ ] `gophish_variables` includes `{{.URL}}` and `{{.Tracker}}`
- [ ] `education_page` and `tags` are populated

### Validation
- [ ] `python3 tools/validate_templates.py --file path/to/template.html` passes with no errors
- [ ] Preview renders correctly: `python3 tools/preview_server.py`

---

## Running the Validator

```bash
# Validate your new template
python3 tools/validate_templates.py --file collaboration/my_template.html

# Validate all templates in a category
python3 tools/validate_templates.py --dir collaboration/

# Validate everything (what CI runs)
python3 tools/validate_templates.py

# See all output including informational notes
python3 tools/validate_templates.py --verbose

# Exit with error code on warnings too (strict mode)
python3 tools/validate_templates.py --strict

# Regenerate the template catalog after adding/editing templates
python3 tools/generate_catalog.py

# Run the tool unit tests (standard library only — no dependencies)
python3 -m unittest discover -s tests -t tests
```

**Passing validator output looks like:**
```
GoPhish Template Validator
Scanning 52 template(s)...

  ✓ PASS  collaboration/slack_notification.html
  ✓ PASS  collaboration/teams_alert.html
  ...

──────────────────────────────────────────────────────
Summary: 52 templates validated
  Passed:   52
──────────────────────────────────────────────────────
✓ All checks passed!
```

---

## Preview Your Template

```bash
python3 tools/preview_server.py
```

Open `http://localhost:8080` to browse all templates in a gallery view. Click **Preview** to see your template with GoPhish variables substituted with realistic sample data.

Use `--name`, `--email`, and `--last-name` flags to customize preview values:

```bash
python3 tools/preview_server.py --name "Alex" --email "alex@example.com"
```

---

## Pull Request Process

1. **One template per PR** (or one category if adding multiple related templates)
2. **PR title format:** `feat: add [Platform] [scenario] template` or `fix: [category] mobile viewport issue`
3. **PR description should include:**
   - What platform/scenario is being simulated
   - Why this attack vector is valuable for security awareness training
   - Difficulty rating and estimated click rate with brief justification
   - Screenshot or description of the template's appearance
4. **CI will automatically run** `validate_templates.py` on your PR — fix any errors before requesting review
5. **Reviews focus on:** accuracy of the attack scenario, quality of educational content, mobile rendering, and GoPhish compatibility

Thank you for making security awareness training better for everyone!
