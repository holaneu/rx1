from dotenv import load_dotenv
import os

load_dotenv()

llm_providers = [
    {
        "name": "openrouter",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key": os.getenv('OPENROUTER_API_KEY'),
        "api_type": "openai"
    },
    {
        "name": "openai",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "api_key": os.getenv('OPENAI_API_KEY'),
        "api_type": "openai"
    },
    {
        "name": "mistral",
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "api_key": os.getenv('MISTRAL_API_KEY'),
        "api_type": "openai"
    },
    {
        "name": "google",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "api_key": os.getenv('GEMINI_API_KEY'),
        "api_type": "openai"
    }
]

# Model Configurations 
llm_models = [
    {
        "name": "openai/gpt-4.1",
        "provider": "openrouter"
    },    
    {
        "name": "openai/gpt-4.1-mini",
        "provider": "openrouter"
    },
    {
        "name": "openai/gpt-4.1-nano",
        "provider": "openrouter"
    },
    {
        "name": "gpt-4.1",
        "provider": "openai"
    },
    {
        "name": "gpt-4.1-mini",
        "provider": "openai"
    },  
    {
        "name": "gpt-4o",
        "provider": "openai"
    },
    {
        "name": "gpt-4o-mini",
        "provider": "openai"
    },
    {
        "name": "o3-mini",
        "provider": "openai"
    },
    {
        "name": "mistral-small-latest",
        "provider": "mistral"
    },
    {
        "name": "mistral-large-latest",
        "provider": "mistral"
    },
    {
        "name": "gemini-2.5-flash",
        "provider": "google"
    },
    {
        "name": "gemini-2.0-flash-lite",
        "provider": "google"
    }
]
