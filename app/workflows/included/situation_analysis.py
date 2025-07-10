from app.workflows.core import *
from app.tools.public import save_to_file, user_files_folder_path
from app.assistants.public import assistant_analyze_situation

@workflow()
def situation_analysis(input, model=None):
    """Analyzes a given situation and provides insights."""
    try:
        wf = Workflow()
        ai_data = wf.get_assistant_output_or_raise(assistant_analyze_situation(input=input.strip(), model=model))
        file_path = user_files_folder_path("situace.txt")
        save_to_file(file_path, ai_data + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=ai_data,
            msgBody=f"Result saved to {file_path}"
        )
    except Exception as e:
        return wf.error_response(error=e)