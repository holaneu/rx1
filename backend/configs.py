from dotenv import load_dotenv
import os

load_dotenv()

# User settings
USER_SETTINGS = {
  "user_id": os.getenv('USER_ID'),
}

# Application Settings
APP_SETTINGS = {
  "user_files_folder_path": f"user/{USER_SETTINGS["user_id"]}/files/test_files",
  "locale_dropbox_path": os.getenv('LOCALE_DROPBOX_PATH'),
}

# Model Configurations 
ai_chat_models = [
  {
    "name": "gpt-4.1",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "api_key": os.getenv('OPENAI_API_KEY'),
    "api_type": "openai",
    "provider": "openai"
  },
  {
    "name": "gpt-4.1-mini",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "api_key": os.getenv('OPENAI_API_KEY'),
    "api_type": "openai",
    "provider": "openai"
  },  
  {
    "name": "gpt-4o",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "api_key": os.getenv('OPENAI_API_KEY'),
    "api_type": "openai",
    "provider": "openai"
  },
  {
    "name": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "api_key": os.getenv('OPENAI_API_KEY'),
    "api_type": "openai",
    "provider": "openai"
  },
  {
    "name": "o3-mini",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "api_key": os.getenv('OPENAI_API_KEY'),
    "api_type": "openai",
    "provider": "openai"
  },
  {
    "name": "mistral-small-latest",
    "base_url": "https://api.mistral.ai/v1/chat/completions",
    "api_key": os.getenv('MISTRAL_API_KEY'),
    "api_type": "openai",
    "provider": "mistral"
  },
  {
    "name": "mistral-large-latest",
    "base_url": "https://api.mistral.ai/v1/chat/completions",
    "api_key": os.getenv('MISTRAL_API_KEY'),
    "api_type": "openai",
    "provider": "mistral"
  },
  {
    "name": "gemini-2.0-flash",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", 
    "api_key": os.getenv('GEMINI_API_KEY'),
    "api_type": "openai",
    "provider": "google"
  },
  {
    "name": "gemini-2.0-flash-lite",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", 
    "api_key": os.getenv('GEMINI_API_KEY'),
    "api_type": "openai",
    "provider": "google"
  },
  {
    "name": "claude-3-haiku",
    "base_url": "https://api.anthropic.com/v1/messages",
    "api_key": os.getenv('ANTHROPIC_API_KEY'),
    "api_type": "anthropic",
    "provider": "anthropic"
  },
  {
    "name": "deepseek-chat",
    "base_url": "https://api.deepseek.com/chat/completions",
    "api_key": os.getenv('DEEPSEEK_CHAT_API_KEY'),
    "api_type": "openai",
    "provider": "deepseek"
  },
  {
    "name": "deepseek-reasoner",
    "base_url": "https://api.deepseek.com/chat/completions",
    "api_key": os.getenv('DEEPSEEK_REASONER_API_KEY'),
    "api_type": "openai",
    "provider": "deepseek"
  }
]