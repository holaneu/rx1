import os
import sys
import ast
import re
import importlib
import importlib.util
from typing import Dict, List, Optional
from app.configs.module_config import ModuleConfig
from app.configs.app_config import APP_SETTINGS, USER_SETTINGS

class ModuleManager:
    """Unified module management for both static imports and dynamic registry loading."""
    
    def __init__(self):
        self.AUTO_START = "# AUTO-GENERATED-IMPORTS-START"
        self.AUTO_END = "# AUTO-GENERATED-IMPORTS-END"
        self.config = ModuleConfig()
    
    def full_reload(self, categories: Optional[List[str]] = None, package_types: Optional[List[str]] = None):
        """
        Complete reload: static imports + registry updates.
        
        Args:
            categories: ["app", "admin", "extensions", "user_custom"] or None for all
            package_types: ["workflows", "assistants", "tools", "prompts"] or None for all
        """
        if not categories:
            categories = ["app", "admin", "extensions", "user_custom"]
        if not package_types:
            package_types = self.config.PACKAGE_TYPES
        
        print(f"Starting full reload for categories: {categories}, packages: {package_types}")
        
        # 1. Update static imports for each category
        for category in categories:
            self._update_static_imports_for_category(category)
        
        # 2. Reload dynamic modules for each package type
        for package_type in package_types:
            registry = self.config.get_registry_for_package(package_type)
            if registry is not None:
                self._load_dynamic_modules_for_package(package_type, registry)
        
        # 3. Invalidate Python import cache
        importlib.invalidate_caches()
        
        print("Full reload completed successfully")
    
    def _update_static_imports_for_category(self, category: str):
        """Update __init__.py files for all packages in a category."""
        category_paths = self.config.get_category_paths(category)
        
        for directory in category_paths:
            if os.path.exists(directory):
                init_path = os.path.join(directory, "__init__.py")
                existing_symbols = self._get_existing_symbols(init_path)
                new_auto_block = self._generate_imports(directory, existing_symbols)
                self._update_init_file(init_path, new_auto_block)
                print(f"Updated static imports: {init_path}")
                
                # Reload the Python module
                try:
                    pkg_name = directory.replace("/", ".").replace("\\", ".")
                    if pkg_name in sys.modules:
                        importlib.reload(sys.modules[pkg_name])
                        print(f"Reloaded Python module: {pkg_name}")
                except Exception as e:
                    print(f"Warning: Could not reload module {pkg_name}: {e}")
    
    def _load_dynamic_modules_for_package(self, package_type: str, registry: Dict[str, dict]):
        """Load user custom modules into registry for a specific package type."""
        # Only load from user_custom directory for dynamic loading
        user_custom_paths = self.config.get_all_module_paths().get("user_custom", {})
        directory = user_custom_paths.get(package_type)
        
        if not directory or not os.path.isdir(directory):
            print(f"No user custom directory found for {package_type}: {directory}")
            return
        
        # Clean existing user modules from registry
        module_prefix = directory.replace("/", ".").replace("\\", ".")
        keys_to_remove = [
            key for key, value in registry.items()
            if isinstance(value, dict) and value.get("module", "").startswith(module_prefix)
        ]
        for key in keys_to_remove:
            del registry[key]
            print(f"Removed old registry entry: {key}")
        
        # Remove from sys.modules
        for module_name in list(sys.modules):
            if module_name.startswith(module_prefix):
                del sys.modules[module_name]
        
        # Load new modules
        self._load_modules_from_directory(directory, package_type)
        print(f"Dynamic modules loaded for {package_type} from {directory}")
    
    def _load_modules_from_directory(self, directory: str, package_type: str):
        """Load all Python modules from a directory."""
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".py") and filename not in {"__init__.py", "core.py", "_core.py"}:
                    rel_path = os.path.relpath(os.path.join(root, filename), directory)
                    parts = ["user_data", USER_SETTINGS.USER_ID, f"custom_{package_type}"] + rel_path.split(os.sep)
                    mod_name = ".".join(parts).rsplit(".py", 1)[0]
                    file_path = os.path.join(root, filename)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(mod_name, file_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            print(f"Loaded dynamic module: {mod_name}")
                    except Exception as e:
                        print(f"Error loading module {mod_name}: {e}")
    
    # Helper methods from original update_init2.py
    def _extract_symbols(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            node = ast.parse(f.read(), filepath)
        symbols = []
        for n in node.body:
            if isinstance(n, ast.FunctionDef):
                symbols.append(n.name)
            elif isinstance(n, ast.ClassDef):
                symbols.append(n.name)
        return symbols

    def _get_existing_symbols(self, init_path):
        if not os.path.exists(init_path):
            return set()
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = re.compile(f"{self.AUTO_START}.*?{self.AUTO_END}", re.DOTALL)
        content_no_auto = pattern.sub("", content)
        match = re.search(r"__all__\s*=\s*\[([^\]]*)\]", content_no_auto)
        if not match:
            return set()
        items = re.findall(r'"([^"]+)"', match.group(1))
        return set(items)

    def _generate_imports(self, directory, existing_symbols):
        import_lines = []
        all_names = []
        for root, _, files in os.walk(directory):
            for fname in sorted(files):
                if fname.endswith(".py") and fname not in ["__init__.py", "core.py", "_core.py"]:
                    filepath = os.path.join(root, fname)
                    symbols = self._extract_symbols(filepath)
                    symbols = [s for s in symbols if not s.startswith("_") and s not in existing_symbols]
                    if symbols:
                        rel_path = os.path.relpath(filepath, directory)
                        parts = rel_path.replace(".py", "").split(os.sep)
                        import_path = ".".join(parts)
                        import_lines.append(f"from .{import_path} import {', '.join(symbols)}")
                        all_names.extend(symbols)
        if not all_names:
            return ""
        imports_block = "\n".join(import_lines)
        all_block = "__all__ = [\n    " + ",\n    ".join(f'"{name}"' for name in all_names) + ",\n]"
        return imports_block + "\n\n" + all_block

    def _update_init_file(self, init_path, new_auto_block):
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(f"{self.AUTO_START}\n{self.AUTO_END}\n")
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = re.compile(f"{self.AUTO_START}.*?{self.AUTO_END}", re.DOTALL)
        if new_auto_block.strip():
            replacement = f"{self.AUTO_START}\n{new_auto_block}\n{self.AUTO_END}"
        else:
            replacement = f"{self.AUTO_START}\n{self.AUTO_END}"
        if pattern.search(content):
            content = pattern.sub(replacement, content)
        else:
            content = f"{replacement}\n\n" + content
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)