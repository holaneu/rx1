from app.workflows.core import workflow, Workflow
from app.assistants.included import assistant_explain_simply_lexicon
from app.tools.included import save_to_file, user_data_files_path

@workflow()
def explain_simply_lexicon(input, model=None):
    """Provides simple explanations, synonyms, and examples for a given phrase."""
    try:
        wf = Workflow()
        ai_data = wf.get_assistant_output_or_raise(assistant_explain_simply_lexicon(input=input.strip(), model=model))
        file_name = "lexicon.txt"
        save_to_file(user_data_files_path(file_name), ai_data + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=ai_data,
            msgBody=f"Result saved to {user_data_files_path(file_name)}"
        )
    except Exception as e:
        return wf.error_response(error=e)
