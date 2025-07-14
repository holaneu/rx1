from app.workflows.core import workflow, Workflow
from app.assistants.included import assistant_assistant_instructions_creator
from app.tools.included import save_to_file, user_data_files_path

@workflow()
def create_assistatnt_prompt(input, model=None):
    """Creates a new assistant based on the input."""
    try:
        wf = Workflow()
        ai_data = wf.get_assistant_output_or_raise(assistant_assistant_instructions_creator(input=input.strip(), model=model))
        file_name = "assistants.txt"
        save_to_file(user_data_files_path(file_name), ai_data + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=ai_data,
            msgBody=f"Result saved to {user_data_files_path(file_name)}"
        )
    except Exception as e:
        return wf.error_response(error=e)
