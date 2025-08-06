
# Expose the registry directly
from .core import WORKFLOWS_REGISTRY

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .included.create_assistatnt_prompt import create_assistatnt_prompt
from .included.download_ai_news import download_ai_news
from .included.explain_simply_lexicon import explain_simply_lexicon
from .included.logbook_entry import logbook_entry
from .included.quiz_from_text import quiz_from_text
from .included.situation_analysis import situation_analysis
from .included.take_quick_note import take_quick_note
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
    "explain_simply_lexicon",
    "logbook_entry",
    "quiz_from_text",
    "situation_analysis",
    "take_quick_note",
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


# Load user-defined modules for this package
from app.utils.custom_imports import import_user_custom_modules
import_user_custom_modules("workflows", WORKFLOWS_REGISTRY)