
# Old settings
USER_SETTINGS_OLD = {
    "user_id": "admin",
}

APP_SETTINGS_OLD = {
    "user_data_path": f"user_data/{USER_SETTINGS_OLD['user_id']}",
    "user_data_files_path": f"user_data/{USER_SETTINGS_OLD["user_id"]}/files",
    "custom_workflows_path_list": ["user_data", USER_SETTINGS_OLD["user_id"], "custom_workflows"]
}

#New settings:
class USER_SETTINGS:
    USER_ID = "admin"

class APP_SETTINGS:
    USER_DATA_PATH = f"user_data/{USER_SETTINGS.USER_ID}"
    USER_DATA_FILES_PATH = f"user_data/{USER_SETTINGS.USER_ID}/files"
    CUSTOM_WORKFLOWS_PATH_LIST = ["user_data", USER_SETTINGS.USER_ID, "custom_workflows"]

