"""
# VERSION 1

import os
import importlib

# Import all Python files in the workflows folder (except __init__.py and registry.py)
module_path = os.path.dirname(__file__)

for filename in os.listdir(module_path):
    if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)

# Optionally expose the registry directly
from .core import TOOLBOX_REGISTRY
"""

"""
# VERSION 2

import os
import importlib
import inspect

__all__ = []

# Subfolders you want to include
subdirs = ["included", "test"]  # You can extend this later

current_dir = os.path.dirname(__file__)
package_base = __name__  # "app.toolbox"

for subdir in subdirs:
    subdir_path = os.path.join(current_dir, subdir)
    if not os.path.isdir(subdir_path):
        continue

    for filename in os.listdir(subdir_path):
        if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
            mod_name = filename[:-3]
            full_module_name = f"{package_base}.{subdir}.{mod_name}"  # e.g., app.toolbox.included.file1
            module = importlib.import_module(full_module_name)

            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) or inspect.isclass(obj):
                    globals()[name] = obj
                    __all__.append(name)
"""