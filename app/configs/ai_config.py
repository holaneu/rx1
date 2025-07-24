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
        "name": "google/gemini-2.5-pro", 
        "provider": "openrouter"
    },
    {
        "name": "google/gemini-2.5-flash", 
        "provider": "openrouter"
    },
    {
        "name": "google/gemini-2.5-flash-lite", 
        "provider": "openrouter"
    },
    {
        "name": "mistralai/mistral-small-3.2-24b-instruct:free", 
        "provider": "openrouter"
    },
    {
        "name": "mistralai/mistral-large-2411", 
        "provider": "openrouter"
    },
    {
        "name": "mistralai/devstral-medium", 
        "provider": "openrouter"
    },
    {
        "name": "mistralai/devstral-small-2505:free", 
        "provider": "openrouter"
    },
    {
        "name": "mistralai/mistral-nemo:free", 
        "provider": "openrouter"
    },
    {
        "name": "anthropic/claude-sonnet-4", 
        "provider": "openrouter"
    },
    {
        "name": "anthropic/claude-3.7-sonnet:beta", 
        "provider": "openrouter"
    },
    {
        "name": "deepseek/deepseek-r1-0528-qwen3-8b:free", 
        "provider": "openrouter"
    },
    {
        "name": "qwen/qwen2.5-vl-32b-instruct:free", 
        "provider": "openrouter"
    },
    {
        "name": "meta-llama/llama-3.3-70b-instruct", 
        "provider": "openrouter"
    },
    {
        "name": "microsoft/phi-4", 
        "provider": "openrouter"
    }
]
