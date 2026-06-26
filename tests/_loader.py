"""Helper to import the (non-package) scripts under tools/ for testing."""
import importlib.util
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"


def load_tool(name):
    """Import tools/<name>.py as a module and return it."""
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
