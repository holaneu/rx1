from workflows.registry import workflow
from tools.tools_default import save_to_file, user_files_folder_path
from assistants.assistants_default import assistant_translator_cs_en
from utils.response_types import response_output_error, response_output_success, ResponseKey, ResponseAction, RaisedError
from utils.shared import put_status_to_queue

@workflow()
def translation_cs_en_basic(task_id, input, model=None):
    """Translates text between Czech and English."""
    try:
        if not input or not input.strip():
            raise RaisedError("Empty input provided")

        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Starting translation process...",
            ResponseKey.BODY: "Connecting to translation assistant"
        })

        result = assistant_translator_cs_en(input=input, model=model)
        translation = result.get("message", {}).get("content", "").strip() if result else ""

        if not translation:
            raise RaisedError("Translation failed or returned empty result")

        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Translation completed",
            ResponseKey.BODY: f"Translated text: {translation}"
        })
        
        file_path = user_files_folder_path("translations.txt")
        save_to_file(user_files_folder_path("translations.txt"), translation + "\n\n-----\n", prepend=True)

        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: f"Translation saved to file",
            ResponseKey.BODY: f"Translation added to the file {file_path}"
        })
        
        return response_output_success({
            ResponseKey.DATA: translation,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.TASK_ID: task_id
        })

    except Exception as e:
        return response_output_error({
            ResponseKey.ERROR: f"Unexpected error: {str(e)}",
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.TASK_ID: task_id
        })
