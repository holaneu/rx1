import os
import importlib

module_path = os.path.dirname(__file__)

# Import all Python files in the workflows folder (except __init__.py and other special files)
for filename in os.listdir(module_path):
    if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)

# Import all Python files from the listed subfolders
# List of subfolders to import Python files from
subfolders = ["included", "custom", "test"]

for subfolder in subfolders:
    subfolder_path = os.path.join(module_path, subfolder)
    if os.path.isdir(subfolder_path):
        for filename in os.listdir(subfolder_path):
            if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
                module_name = f"{__name__}.{subfolder}.{filename[:-3]}"
                importlib.import_module(module_name)

# Expose directly
from .core import WORKFLOWS_REGISTRY

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---


# --- Import user's custom workflows from user_data ---
def import_user_custom_workflows():
    try:
        import importlib.util
        import os
        import sys
        from .core import WORKFLOWS_REGISTRY  
        from app.configs.app_config import APP_SETTINGS

        custom_wf_path_list = APP_SETTINGS.CUSTOM_WORKFLOWS_PATH_LIST #["user_data", "<user_id - admin>", "custom_workflows"]
        custom_wf_path_str = ".".join(custom_wf_path_list)

        # Selectively clear registry entries from user's custom workflow modules
        keys_to_remove = [
            key for key, value in WORKFLOWS_REGISTRY.items()
            if isinstance(value, dict) and value.get("module", "").startswith(custom_wf_path_str)
        ]
        for key in keys_to_remove:
            del WORKFLOWS_REGISTRY[key]

        # Clear previously loaded user's custom workflow modules
        for module_name in list(sys.modules):
            if module_name.startswith(custom_wf_path_str):
                del sys.modules[module_name]
        
        user_wf_dir = os.path.join(os.getcwd(), *custom_wf_path_list)
        if not os.path.isdir(user_wf_dir):
            return

        for filename in os.listdir(user_wf_dir):
            if filename.endswith(".py") and filename not in {"__init__.py", "core.py"}:
                module_name = f"{custom_wf_path_str}.{filename[:-3]}"
                file_path = os.path.join(user_wf_dir, filename)
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error importing user custom workflows: {e}")
        raise e

# Import it immediately
import_user_custom_workflows()
