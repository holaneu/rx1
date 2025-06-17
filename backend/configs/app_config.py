from dotenv import load_dotenv
import os

load_dotenv()

# User settings
USER_SETTINGS = {
  "user_id": os.getenv('USER_ID'),
}

# Application Settings
APP_SETTINGS = {
  "user_files_folder_path": f"user/{USER_SETTINGS["user_id"]}/files",
  "locale_dropbox_path": os.getenv('LOCALE_DROPBOX_PATH'),
}
