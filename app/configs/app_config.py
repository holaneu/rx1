# settings:

class USER_SETTINGS:
    USER_ID = "admin"

class APP_SETTINGS:
    USER_DATA_PATH = f"user_data/{USER_SETTINGS.USER_ID}"
    USER_DATA_FILES_PATH = f"user_data/{USER_SETTINGS.USER_ID}/files"
    CUSTOM_WORKFLOWS_PATH_LIST = ["user_data", USER_SETTINGS.USER_ID, "custom_workflows"]

