from app.workflows.core import *

@workflow()
def take_quick_note(input, task_id, model=None):
    """Takes a quick note and saves it to both JSON database and file."""
    try:
        from app.tools import save_to_file, user_data_files_path, json_db_add_entry
        
        wf = Workflow(task_id=task_id)

        note = input.strip()

        db_entry = {
            "content": note
        }
        
        file_path = user_data_files_path("quick_notes.md")
        db_file_path = user_data_files_path("databases/quick_notes.json")

        save_db_result = json_db_add_entry(db_filepath=db_file_path, collection="notes", entry=db_entry)
        wf.log_msg(msg=save_db_result["message"])

        save_file_result = save_to_file(filepath=file_path, content=note, prepend=True, delimiter="-----")
        wf.log_msg(msg=save_file_result["message"])

        return wf.success_response(
            data=note,
        )
    
    except Exception as e:
        return wf.error_response(error=e)