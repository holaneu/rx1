from app.workflows.core import *
from app.tools.included import save_to_file, user_data_files_path
from app.assistants.included import assistant_translator_cs_en

@workflow()
def translation_cs_en_basic(task_id, input, model=None):
    """Translates text between Czech and English v2."""
    try:
        wf = Workflow()

        wf.add_to_func_log(msgTitle="Workflow Started", msgBody=f"Task ID: {task_id}, Input: {input}, Model: {model}")

        translated_text = wf.get_assistant_output_or_raise(assistant_translator_cs_en(input=input, model=model))
        
        wf.add_to_func_log(msgTitle="Translation Completed", msgBody=f"Translated text: {translated_text}")
        
        file_path = user_data_files_path("translations.txt")
        save_to_file(file_path, translated_text + "\n\n-----\n", prepend=True)
        
        wf.add_to_func_log(msgTitle="Translation Saved to File", msgBody=f"File path: {file_path}")
        
        return wf.success_response(
            data=translated_text,
            msgBody=f"Result saved to {file_path}"
        )

    except Exception as e:
        return wf.error_response(error=e)