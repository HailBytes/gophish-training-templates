# `tools` — Maintenance scripts

Python utilities for validating, previewing, importing, and documenting the templates. No third-party dependencies are required for the generators/validator (standard library only).

Part of [gophish-training-templates](../README.md).

## Scripts

| Script | What it does |
|---|---|
| [`generate_catalog.py`](generate_catalog.py) | Builds [`docs/CATALOG.md`](../docs/CATALOG.md) from every category `metadata.json`. `--check` fails if the committed catalog is stale; `--stdout` prints without writing. |
| [`generate_folder_readmes.py`](generate_folder_readmes.py) | Writes each category's `README.md` from its `metadata.json`. Same `--check` / `--stdout` flags. |
| [`validate_templates.py`](validate_templates.py) | Lints templates (e.g. required GoPhish variables, well-formed HTML, metadata consistency). |
| [`preview_server.py`](preview_server.py) | Serves the templates locally in a browser for visual review. |
| [`import_to_gophish.py`](import_to_gophish.py) | Imports templates into a running GoPhish instance via its API. |

## Regenerating docs

```bash
python3 tools/generate_catalog.py          # docs/CATALOG.md
python3 tools/generate_folder_readmes.py    # <category>/README.md
```

Both are deterministic (no wall-clock date embedded), so the output can be committed and checked in CI with `--check`.

> Note: `<category>/README.md` files are generated. Edit `metadata.json` (or the generator) and regenerate — don't hand-edit the generated READMEs.
