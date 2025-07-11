
import os
import importlib
import inspect

__all__ = []

# Directory of this file
_current_dir = os.path.dirname(__file__)
_package_base = __name__ 

for filename in os.listdir(_current_dir):
    if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
        module_name = filename[:-3]
        full_module_name = f"{_package_base}.{module_name}"

        module = importlib.import_module(full_module_name)

        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                globals()[name] = obj
                __all__.append(name)
