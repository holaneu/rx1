
# Expose the registry directly
from .core import PROMPTS_REGISTRY

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .included import prompt_example, output_without_comments, do_task, correct_grammar
from .test.test import test
from .test.test2 import test2

__all__ = [
    "prompt_example",
    "output_without_comments",
    "do_task",
    "correct_grammar",
    "test",
    "test2",
]
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---


# Load user-defined modules for this package
from app.utils.custom_imports import import_user_custom_modules
import_user_custom_modules("prompts", PROMPTS_REGISTRY)