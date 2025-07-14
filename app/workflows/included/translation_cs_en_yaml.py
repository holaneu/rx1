from app.workflows.core import *
from app.tools.included import save_to_file, user_data_files_path
from app.assistants.included import assistant_translator_cs_en_yaml

@workflow()
def translation_cs_en_yaml(input, model=None):
    """Translates text between Czech and English in YAML format."""
    try:
        wf = Workflow()
        ai_data = wf.get_assistant_output_or_raise(assistant_translator_cs_en_yaml(input=input.strip(), model=model))
        file_path = user_data_files_path("vocabulary_yaml.txt")
        save_to_file(file_path, ai_data + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=ai_data,
            msgBody=f"Result saved to {file_path}"
        )
    except Exception as e:
        return wf.error_response(error=e)