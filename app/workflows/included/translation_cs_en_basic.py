from app.workflows.core import *

@workflow()
def translation_cs_en_basic(task_id, input, model="openai/gpt-4.1"):
    """Translates text between Czech and English v2."""
    try:
        from app.tools.included import save_to_file, user_data_files_path
        from app.assistants.included import translator_cs_en
        
        wf = Workflow()

        wf.add_msg_to_log(msgTitle="Workflow Started", msgBody=f"Task ID: {task_id}, Input: {input}, Model: {model}")

        translated_text = wf.get_assistant_output_or_raise(translator_cs_en(input=input, model=model))
        
        wf.add_msg_to_log(msgTitle="LLM: Translated text", msgBody=translated_text)
        
        file_path = user_data_files_path("translations.txt")
        save_file_result = save_to_file(file_path, translated_text, delimiter="-----", prepend=True)
        wf.add_msg_to_log(msg=save_file_result["message"])
        
        return wf.success_response(
            data=translated_text,
            msgBody=f"Result saved to {file_path}"
        )

    except Exception as e:
        return wf.error_response(error=e)