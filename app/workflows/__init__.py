import os
import importlib

module_path = os.path.dirname(__file__)

# Import all Python files in the workflows folder (except __init__.py and other special files)
for filename in os.listdir(module_path):
    if filename.endswith(".py") and filename not in {"__init__.py"}:
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)

# Import all Python files from the listed subfolders
# List of subfolders to import Python files from
subfolders = ["included", "test"]

for subfolder in subfolders:
    subfolder_path = os.path.join(module_path, subfolder)
    if os.path.isdir(subfolder_path):
        for filename in os.listdir(subfolder_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"{__name__}.{subfolder}.{filename[:-3]}"
                importlib.import_module(module_name)

# Expose directly
from .core import WORKFLOWS_REGISTRY
#from .core import workflow
#from .core import Workflow
#__all__ = ["WORKFLOWS_REGISTRY", "workflow", "Workflow"]