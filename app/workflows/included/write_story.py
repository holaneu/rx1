from app.workflows.core import workflow, Workflow
from app.assistants.public import assistant_writer
from app.tools.public import save_to_file, json_db_add_entry, user_files_folder_path

@workflow()
def write_story(input, model=None):
    """Generates short feel-good stories."""
    try:
        wf = Workflow()
        story = wf.get_assistant_output_or_raise(assistant_writer(input=input.strip(), model=model))
        save_to_file(user_files_folder_path("stories.md"), story + "\n\n-----\n", prepend=True)
        json_db_add_entry(
            db_filepath=user_files_folder_path("databases/stories.json"),
            collection="entries",
            entry={"input": input.strip(), "content": story},
            add_createdat=True
        )
        return wf.success_response(
            data=story,
            msgBody=f"Story saved to {user_files_folder_path('stories.md')}"
        )
    except Exception as e:
        return wf.error_response(error=e)
