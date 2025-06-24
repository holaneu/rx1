from workflows.core import *
from tools.tools_default import save_to_file, user_files_folder_path
from assistants.assistants_default import assistant_translator_cs_en

@workflow()
def translation_cs_en_basic2(task_id, input, model=None):
    """Translates text between Czech and English v2."""
    try:
        wf = Workflow()
        wf.add_func_log(title="Translation Workflow Started", body=f"Task ID: {task_id}, Input: {input}, Model: {model}")

        translation = assistant_translator_cs_en(input=input, model=model)
        translated_text = wf.get_assistant_output_or_raise(translation)
        
        wf.add_func_log(title="Translation Completed", body=f"Translated text: {translated_text}")
        
        file_path = user_files_folder_path("translations.txt")
        save_to_file(user_files_folder_path("translations.txt"), translated_text + "\n\n-----\n", prepend=True)
        
        wf.add_func_log(title="Translation Saved to File", body=f"File path: {file_path}")
        
        return wf.workflow_success(
            data=translated_text,
            msgTitle="Translation Completed",
            msgBody=f"Translated text saved to {file_path}"
        )

    except Exception as e:
        return wf.workflow_error(
            error=e,
            msgTitle="Translation Workflow Error",
            msgBody=f"An error occurred during translation: {str(e)}"
        )