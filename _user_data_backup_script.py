import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load .env from app/.env
dotenv_path = os.path.join('app', '.env')
load_dotenv(dotenv_path)

def backup_user_data(source_folder, base_destination_folder, ignore_names=None):
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    last_folder = os.path.basename(os.path.normpath(source_folder))
    destination_folder = os.path.join(base_destination_folder, now_str, last_folder)

    def ignore_func(dir, files):
        return [name for name in files if any(ignore in name.lower() for ignore in ignore_names)]

    try:
        shutil.copytree(
            src=source_folder,
            dst=destination_folder,
            ignore=ignore_func if ignore_names else None
        )
        print(f"✅ Backup completed: {destination_folder}")
    except Exception as e:
        print(f"❌ Error during backup: {e}")

# === CONFIGURATION ===

# Get absolute path to the directory containing this script
app_root = os.path.abspath(os.path.dirname(__file__))

# Get external storage path from .env
external_storage = os.getenv('EXTERNAL_STORAGE_1_LOCAL_PATH')

# Compose destination base path
destination_base_path = os.path.join(external_storage, '__projects_new', 'rx1', '_backups')

# Define the source path — use app_root or modify as needed
source_path = os.path.join(app_root)  # or os.path.join(app_root, 'user_data')

# Ignore list for files/folders
ignore_list = ['__pycache__', '.git', '.idea', '.vscode']

# Run the backup
backup_user_data(
    source_folder=source_path, 
    base_destination_folder=destination_base_path,
    ignore_names=ignore_list
    )
