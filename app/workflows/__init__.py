
# Expose directly
from ._core import workflow, Workflow

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .included.create_assistatnt_prompt import create_assistatnt_prompt
from .included.download_ai_news import download_ai_news
from .included.edu_cards_selection import edu_cards_selection
from .included.exctract_theses import exctract_theses
from .included.explain_simply_lexicon import explain_simply_lexicon
from .included.logbook_entry import logbook_entry
from .included.quiz_from_text import quiz_from_text
from .included.situation_analysis import situation_analysis
from .included.take_quick_note import take_quick_note
from .included.tech_vocabulary_auto_update import tech_vocabulary_auto_explain
from .included.text_summarization import text_summarization
from .included.translation_cs_en_basic import translation_cs_en_basic
from .included.translation_cs_en_json import translation_cs_en_json
from .included.translation_cs_en_yaml import translation_cs_en_yaml
from .included.video_transcript_summarization import video_transcript_summarization
from .included.write_story import write_story
from .included.write_story_reviewed import write_story_reviewed

__all__ = [
    "create_assistatnt_prompt",
    "download_ai_news",
    "edu_cards_selection",
    "exctract_theses",
    "explain_simply_lexicon",
    "logbook_entry",
    "quiz_from_text",
    "situation_analysis",
    "take_quick_note",
    "tech_vocabulary_auto_explain",
    "text_summarization",
    "translation_cs_en_basic",
    "translation_cs_en_json",
    "translation_cs_en_yaml",
    "video_transcript_summarization",
    "write_story",
    "write_story_reviewed",
]
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---

# Load user-defined modules for this package using new system
from app.configs.module_config import ModuleConfig
config = ModuleConfig()
registry = config.get_registry_for_package("workflows")
if registry is not None:
    from app.utils.module_manager import ModuleManager
    manager = ModuleManager()
    manager._load_dynamic_modules_for_package("workflows", registry)