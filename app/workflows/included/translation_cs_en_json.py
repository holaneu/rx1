from app.workflows import workflow, Workflow

@workflow()
def translation_cs_en_json(input, task_id, model="openai/gpt-4.1"):
    """Translates text between Czech and English and outputs it in JSON format."""    
    try:
        from app.tools import save_to_file, user_data_files_path, json_db_add_entry
        from app.assistants import translator_cs_en_json
        import json

        # REMOVE:
        from user_data.admin.custom_tools import test_generate_uuid

        wf = Workflow(task_id=task_id)

        wf.log_msg(msgTitle="Workflow Started", msgBody=f"Task ID: {task_id}, Model: {model}")

        wf.log_msg(msgTitle="Test data", msgBody=f"Uid: {test_generate_uuid()}")
        
        ai_data = wf.get_assistant_output_or_raise(translator_cs_en_json(input=input.strip(), model=model, structured_output=True))

        wf.log_msg(msgTitle="LLM: Translation generated", msgBody=ai_data)

        ai_data_parsed = json.loads(ai_data)        
        if not isinstance(ai_data_parsed, dict):
          raise Exception("invalid JSON structure")
        
        ai_data_readable = json.dumps(ai_data_parsed, indent=2, ensure_ascii=False)
        
        user_input_form = [
            #{"type": "text", "name": "user_name", "label": "What is your name?", "placeholder": "e.g., Jane Doe", "required": True},
            #{"type": "textarea", "name": "feedback", "label": "Please provide your feedback:"},
            {"type": "select", "name": "file-save-confirm", "label": "Do you want to save it to file?", "options": ["Yes", "No"], "required": True},
            {"type": "select", "name": "db-save-confirm", "label": "Do you want to save it to DB?", "options": ["Yes", "No"], "required": True}
        ]

        user_input1 = yield wf.interaction_request(
            msgTitle="Confirmation required",
            msgBody="Please confirm if you want to save the result to file and database.",
            form_elements=user_input_form
        )

        file_name = "vocabulary"

        if user_input1.get("file-save-confirm") == "Yes":
            save_file_result = save_to_file(user_data_files_path(f"{file_name}.md"), ai_data_readable, delimiter="-----", prepend=True)
            wf.log_msg(msg=save_file_result["message"])
        
        if user_input1.get("db-save-confirm") == "Yes":
            save_db_result = json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=ai_data_parsed, add_createdat=True)
            wf.log_msg(msg=save_db_result["message"])  

        return wf.success_response(
            data=ai_data_parsed,
        )
    
    except Exception as e:
        return wf.error_response(error=e)