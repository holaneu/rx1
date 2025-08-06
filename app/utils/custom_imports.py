import os
import sys
import importlib.util
from typing import Dict

from app.configs.app_config import APP_SETTINGS, USER_SETTINGS


def import_user_custom_modules(package_name: str, registry: Dict[str, dict]) -> None:
    """Load user-defined modules for a package and merge them into its registry."""
    if package_name not in getattr(APP_SETTINGS, "CUSTOM_MODULES_FOLDERS", []):
        return

    path_parts = ["user_data", USER_SETTINGS.USER_ID, f"custom_{package_name}"]
    module_prefix = ".".join(path_parts)
    directory = os.path.join(os.getcwd(), *path_parts)
    if not os.path.isdir(directory):
        return

    keys_to_remove = [
        key
        for key, value in registry.items()
        if isinstance(value, dict) and value.get("module", "").startswith(module_prefix)
    ]
    for key in keys_to_remove:
        del registry[key]

    for module_name in list(sys.modules):
        if module_name.startswith(module_prefix):
            del sys.modules[module_name]

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
                rel_path = os.path.relpath(os.path.join(root, filename), directory)
                parts = path_parts + rel_path.split(os.sep)
                mod_name = ".".join(parts).rsplit(".py", 1)[0]
                file_path = os.path.join(root, filename)
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)