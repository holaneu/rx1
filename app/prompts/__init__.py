
# Expose directly
from ._core import prompt, render_prompt_with_context

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .included import prompt_example, output_without_comments, do_task, correct_grammar, explain_swe_terms
from .test.test import test
from .test.test2 import test2

__all__ = [
    "prompt_example",
    "output_without_comments",
    "do_task",
    "correct_grammar",
    "explain_swe_terms",
    "test",
    "test2",
]
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---


# Load user-defined modules for this package using new system
from app.configs.module_config import ModuleConfig
config = ModuleConfig()
registry = config.get_registry_for_package("prompts")
if registry is not None:
    from app.utils.module_manager import ModuleManager
    manager = ModuleManager()
    manager._load_dynamic_modules_for_package("prompts", registry)