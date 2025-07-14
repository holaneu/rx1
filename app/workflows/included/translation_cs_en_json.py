from app.workflows.core import *
from app.tools.included import save_to_file, user_data_files_path, json_db_add_entry
from app.assistants.included import assistant_translator_cs_en_json
import json

@workflow()
def workflow_translation_cs_en_json(input, model=None):
    """Translates text between Czech and English and outputs it in JSON format."""    
    try:
        wf = Workflow()
        ai_data = wf.get_assistant_output_or_raise(assistant_translator_cs_en_json(input=input.strip(), model=model, structured_output=True))
        ai_data_parsed = json.loads(ai_data)        
        if not isinstance(ai_data_parsed, dict):
          raise Exception("invalid JSON structure")
        ai_data_readable = json.dumps(ai_data_parsed, indent=2, ensure_ascii=False)
        file_name = "vocabulary"
        save_to_file(user_data_files_path(f"{file_name}.md"), ai_data_readable + "\n\n-----\n", prepend=True)
        json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=ai_data_parsed, add_createdat=True)
        return wf.success_response(
            data=ai_data_parsed,
            msgBody=f"Result saved to {user_data_files_path(f'{file_name}.md')}"
        )
    except Exception as e:
        return wf.error_response(error=e)