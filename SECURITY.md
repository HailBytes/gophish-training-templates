# Security Policy

This repository contains phishing simulation templates and supporting tooling
(`tools/`) intended for **authorized security awareness training only**. We
treat vulnerabilities in the tooling — and content issues that could enable
real-world harm — seriously.

## Supported Versions

This repo is not versioned/released in the traditional sense; only the latest
commit on `main` is supported. Please make sure you're on the latest `main`
before reporting an issue.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report it privately using one of these channels:

- **Preferred:** [GitHub Security Advisories](../../security/advisories/new)
  for this repository.
- **Email:** security@hailbytes.com

When reporting, please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce (affected file/script, inputs, expected vs. actual
  behavior).
- Whether it affects the tooling in `tools/` (e.g. `import_to_gophish.py`,
  `preview_server.py`, `validate_templates.py`) or the template/landing-page
  HTML itself.

### What to expect

- We aim to acknowledge reports within **5 business days**.
- We'll work with you to confirm the issue, assess severity, and agree on a
  disclosure timeline before any public advisory is published.
- Credit is given to reporters in the advisory unless you prefer to remain
  anonymous.

## Scope

In scope:

- The Python tooling under `tools/` (e.g. path handling in
  `preview_server.py`, API/network handling in `import_to_gophish.py`,
  parsing logic in `validate_templates.py`, `generate_catalog.py`,
  `generate_folder_readmes.py`).
- CI/CD workflow definitions under `.github/workflows/`.
- Template or landing-page HTML that could be used to compromise a system
  running it (e.g. XSS against the GoPhish admin UI, SSRF via `redirect_url`
  handling, credential exfiltration outside the intended GoPhish flow).

Out of scope:

- The fact that these templates simulate phishing/smishing/quishing content —
  that's the intended purpose of this project when used for authorized
  training.
- Vulnerabilities in GoPhish itself (report those to the
  [GoPhish project](https://github.com/gophish/gophish)) or in HailBytes SAT
  (report those to security@hailbytes.com as a product issue, not via this
  repo).

## Responsible Use

These templates are provided for **authorized** security awareness training
only. Do not use them against systems or people without explicit permission.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the full acceptable-use terms that
apply to contributions.
