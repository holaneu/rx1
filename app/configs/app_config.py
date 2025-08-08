import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# settings:

class USER_SETTINGS:
    USER_ID = "admin" # !!! Don't change this value !!!

class APP_SETTINGS:
    USER_DATA_PATH = f"user"
    USER_DATA_FILES_PATH = f"user/files"
    EXTERNAL_STORAGE_1_LOCAL_PATH = os.getenv("EXTERNAL_STORAGE_1_LOCAL_PATH")
    CUSTOM_MODULES_FOLDERS = ["workflows", "assistants", "prompts", "tools"]
    CUSTOM_WORKFLOWS_PATH_LIST = ["user_data", USER_SETTINGS.USER_ID, "custom_workflows"]    
    
