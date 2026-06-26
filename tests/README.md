# `tests` — Test suite

Tests for the maintenance scripts in [`../tools/`](../tools/). Run from the repository root.

Part of [gophish-training-templates](../README.md).

## Running

```bash
python3 -m pytest tests/        # or: python3 -m unittest discover tests
```

## Contents

| File | Covers |
|---|---|
| [`test_validate_templates.py`](test_validate_templates.py) | The template validator/linter. |
| [`test_import_to_gophish.py`](test_import_to_gophish.py) | The GoPhish import tool. |
| [`test_preview_server.py`](test_preview_server.py) | The local preview server. |
| `_loader.py` | Shared test helpers / fixtures. |
