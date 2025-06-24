import os
import importlib

# Import all Python files in the workflows folder (except __init__.py and registry.py)
module_path = os.path.dirname(__file__)

for filename in os.listdir(module_path):
    if filename.endswith(".py") and filename not in {"__init__.py", "registry.py"}:
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)

# Optionally expose the registry directly
from .core import WORKFLOWS_REGISTRY
