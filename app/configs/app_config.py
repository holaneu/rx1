from dotenv import load_dotenv
import os

load_dotenv()

# User settings
USER_SETTINGS = {
    "user_id": "test_user",
}

# Application Settings
APP_SETTINGS = {
    "user_data_path": f"user_data/{USER_SETTINGS['user_id']}",
    "user_data_files_path": f"user_data/{USER_SETTINGS["user_id"]}/files",
    "user_files_folder_path": f"user_data/{USER_SETTINGS["user_id"]}/files"
}
