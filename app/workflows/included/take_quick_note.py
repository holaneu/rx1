from app.workflows.core import *
from app.tools.included import save_to_file, user_data_files_path, json_db_add_entry


@workflow()
def take_quick_note(input, model=None):
    """Takes a quick note and saves it to both JSON database and file."""
    try:
        wf = Workflow()
        if input is None or input.strip() == "":
            raise Exception("No input provided for quick note.")
        note = input.strip()
        db_entry = {
            "content": note
        }
        file_path = user_data_files_path("quick_notes.md")
        db_file_path = user_data_files_path("databases/quick_notes.json")
        json_db_add_entry(db_filepath=db_file_path, collection="notes", entry=db_entry)
        save_to_file(file_path, note + "\n\n-----\n", prepend=True)
        #save_to_external_file("quick_notes_2025_H1_test.md", input.strip() + "\n\n-----\n", prepend=True) 
        return wf.success_response(
            data=note,
            msgBody=f"Result saved to {file_path} and also to the database file {db_file_path}."
        )
    except Exception as e:
        return wf.error_response(error=e)