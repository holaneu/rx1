# app/utils/init_updater.py
import os
import re
import ast
import importlib

AUTO_START = "# AUTO-GENERATED-IMPORTS-START"
AUTO_END = "# AUTO-GENERATED-IMPORTS-END"

APP_DIRS = [
    "app/assistants",    
    "app/prompts",
    "app/tools",
    "app/workflows",
]

ADMIN_DIRS = [
    "user_data/admin/custom_assistants",
    #"user_data/admin/custom_prompts",
    "user_data/admin/custom_tools",
    "user_data/admin/custom_workflows",    
]

EXTENSION_DIRS = [
    "user_data/extensions/assistants",
    "user_data/extensions/prompts",
    "user_data/extensions/tools",
    "user_data/extensions/workflows",    
]

def extract_symbols(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filepath)
    symbols = []
    for n in node.body:
        if isinstance(n, ast.FunctionDef):
            symbols.append(n.name)
        elif isinstance(n, ast.ClassDef):
            symbols.append(n.name)
    return symbols

def get_existing_symbols(init_path):
    if not os.path.exists(init_path):
        return set()
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(f"{AUTO_START}.*?{AUTO_END}", re.DOTALL)
    content_no_auto = pattern.sub("", content)
    match = re.search(r"__all__\s*=\s*\[([^\]]*)\]", content_no_auto)
    if not match:
        return set()
    items = re.findall(r'"([^"]+)"', match.group(1))
    return set(items)

def generate_imports(directory, existing_symbols):
    import_lines = []
    all_names = []
    for root, _, files in os.walk(directory):
        for fname in sorted(files):
            if fname.endswith(".py") and fname not in ["__init__.py", "core.py", "_core.py"]:
                filepath = os.path.join(root, fname)
                symbols = extract_symbols(filepath)
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

def update_init_file(init_path, new_auto_block):
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f"{AUTO_START}\n{AUTO_END}\n")
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(f"{AUTO_START}.*?{AUTO_END}", re.DOTALL)
    if new_auto_block.strip():
        replacement = f"{AUTO_START}\n{new_auto_block}\n{AUTO_END}"
    else:
        replacement = f"{AUTO_START}\n{AUTO_END}"
    if pattern.search(content):
        content = pattern.sub(replacement, content)
    else:
        content = f"{replacement}\n\n" + content
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_inits(target):
    if (target == "user_data_extensions_dirs"):
        target_dirs = EXTENSION_DIRS
    if (target == "user_data_admin_dirs"):
        target_dirs = ADMIN_DIRS
    if (target == "app_dirs"):
        target_dirs = APP_DIRS
    else:
        print("Error: No update target recognized.")

    for directory in target_dirs: #APP_DIRS + EXTENSION_DIRS:
        init_path = os.path.join(directory, "__init__.py")
        existing_symbols = get_existing_symbols(init_path)
        new_auto_block = generate_imports(directory, existing_symbols)
        update_init_file(init_path, new_auto_block)
        print(f"Updated {init_path}")

    # Optionally reload packages dynamically after updating
    for pkg_dir in target_dirs: #APP_DIRS + EXTENSION_DIRS:
        pkg_name = pkg_dir.replace("/", ".")
        try:
            importlib.reload(importlib.import_module(pkg_name))
            print(f"Reloaded package {pkg_name}")
        except ModuleNotFoundError:
            pass
