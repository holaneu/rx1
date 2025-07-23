from app.workflows.core import workflow, Workflow
from app.assistants.included import assistant_writer
from app.tools.included import save_to_file, json_db_add_entry, user_data_files_path

@workflow()
def write_story(input, task_id, model="openai/gpt-4.1"):
    """Generates short feel-good stories."""
    try:
        wf = Workflow(task_id=task_id)
        
        story = wf.get_assistant_output_or_raise(assistant_writer(input=input.strip(), model=model))
        wf.add_msg_to_log(msgTitle="LLM: Story generated", msgBody=story)

        user_input_form = [
            #{"type": "text", "name": "user_name", "label": "What is your name?", "placeholder": "e.g., Jane Doe", "required": True},
            #{"type": "textarea", "name": "feedback", "label": "Please provide your feedback:"},
            {"type": "select", "name": "save-confirm", "label": "Do you want to save it?", "options": ["Yes", "No"], "required": True}
        ]
        user_input1 = yield wf.interaction_request(
            msgTitle="Confirmation required",
            msgBody="Do you want to save the result to file?",
            form_elements=user_input_form
        )

        if user_input1.get("save-confirm") != "Yes":
            return wf.warning_response(
                data=story,
                msgBody="Note: Result not saved to file."
            )

        save_file_result = save_to_file(user_data_files_path("stories.md"), story + "\n\n-----\n", prepend=True)
        wf.add_msg_to_log(msg=save_file_result["message"])

        user_input2 = yield wf.interaction_request(
            msgTitle="Confirmation required",
            msgBody="Do you want to save the result to json db file?",
            form_elements=user_input_form
        )

        if user_input2.get("save-confirm") != "Yes":
            return wf.warning_response(
                data=story,
                msgBody="Note: Result not saved to json db file."
            )

        save_db_result = json_db_add_entry(
            db_filepath=user_data_files_path("databases/stories.json"),
            collection="entries",
            entry={"input": input.strip(), "content": story},
            add_createdat=True
        )
        wf.add_msg_to_log(msg=save_db_result["message"])

        return wf.success_response(
            data=story
        )
    
    except Exception as e:
        return wf.error_response(error=e)
