# Expose the registry directly
from ._core import tool

# --- STATIC IMPORTS (Auto-generated section starts) ---
# AUTO-GENERATED-IMPORTS-START
from .deprecated import call_api_of_type_openai_official, call_api_of_type_anthropic
from .included import formatted_datetime, get_llm_model_info, get_llm_provider_info, format_str_as_llm_message_obj, fetch_llm, call_api_of_type_openai_choices_direct, assistant_output_formatted, download_news_newsapi, open_file, save_to_file, save_to_external_file, save_to_external_file2, save_to_json_file, split_clean, generate_id, current_datetime_iso, user_data_files_path, user_data_path, json_db_load, json_db_save, json_db_create_db_without_schema, json_db_get_entry, json_db_get_collection, json_db_add_entry, json_db_update_entry, json_db_delete_entry, brave_search, download_web_sourcecode, download_web_readable_content, crawl_website_for_urls, extract_urls_from_pages, slugify, encode_image_to_base64, extract_text_from_image_mistral_ocr, extract_text_from_image_openai, commit_to_github

__all__ = [
    "call_api_of_type_openai_official",
    "call_api_of_type_anthropic",
    "formatted_datetime",
    "get_llm_model_info",
    "get_llm_provider_info",
    "format_str_as_llm_message_obj",
    "fetch_llm",
    "call_api_of_type_openai_choices_direct",
    "assistant_output_formatted",
    "download_news_newsapi",
    "open_file",
    "save_to_file",
    "save_to_external_file",
    "save_to_external_file2",
    "save_to_json_file",
    "split_clean",
    "generate_id",
    "current_datetime_iso",
    "user_data_files_path",
    "user_data_path",
    "json_db_load",
    "json_db_save",
    "json_db_create_db_without_schema",
    "json_db_get_entry",
    "json_db_get_collection",
    "json_db_add_entry",
    "json_db_update_entry",
    "json_db_delete_entry",
    "brave_search",
    "download_web_sourcecode",
    "download_web_readable_content",
    "crawl_website_for_urls",
    "extract_urls_from_pages",
    "slugify",
    "encode_image_to_base64",
    "extract_text_from_image_mistral_ocr",
    "extract_text_from_image_openai",
    "commit_to_github",
]
# AUTO-GENERATED-IMPORTS-END
# --- END OF AUTO GENERATED ---


# Load user-defined modules for this package using new system
from app.configs.module_config import ModuleConfig, PackageTypes
config = ModuleConfig()
registry = config.get_registry_for_package(PackageTypes.TOOLS.value)  # Use .value to get string
if registry is not None:
    from app.utils.module_manager import ModuleManager
    manager = ModuleManager()
    manager._load_dynamic_modules_for_package(PackageTypes.TOOLS.value, registry)  # Use .value