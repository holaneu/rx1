
# Expose the registry directly
from ._core import assistant

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .included import translator_cs_en_json, translator_cs_en_yaml, translator_cs_en, summarize_text_key_takeaways, analyze_situation, summarize_video_transcript, explain_simply_lexicon, assistant_instructions_creator, generate_random_poem, generate_short_story, analyze_text_attributes, generate_questions, universal_no_instructions, writer, sarcastic_tech_editor, writer, sarcastic_tech_editor

__all__ = [
    "translator_cs_en_json",
    "translator_cs_en_yaml",
    "translator_cs_en",
    "summarize_text_key_takeaways",
    "analyze_situation",
    "summarize_video_transcript",
    "explain_simply_lexicon",
    "assistant_instructions_creator",
    "generate_random_poem",
    "generate_short_story",
    "analyze_text_attributes",
    "generate_questions",
    "universal_no_instructions",
    "writer",
    "sarcastic_tech_editor",
    "writer",
    "sarcastic_tech_editor",
]
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---


# Load user-defined modules for this package using new system
from app.configs.module_config import ModuleConfig
config = ModuleConfig()
registry = config.get_registry_for_package("assistants")
if registry is not None:
    from app.utils.module_manager import ModuleManager
    manager = ModuleManager()
    manager._load_dynamic_modules_for_package("assistants", registry)
