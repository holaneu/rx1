from app.workflows import workflow, Workflow


@workflow()
def tech_vocabulary_auto_explain(task_id, model="mistralai/mistral-small-3.2-24b-instruct:free"):
    """Auto explain technical vocabulary terms from a file."""
    from app.tools import open_file, split_clean, fetch_llm, save_to_external_file2
    from app.prompts import explain_swe_terms
    from app.configs.app_config import APP_SETTINGS

    from pathlib import Path
    import os

    wf = Workflow(task_id=task_id)    

    files_folder_root = APP_SETTINGS.EXTERNAL_STORAGE_1_LOCAL_PATH
    files_folder_path = "_knowledge_base"
    input_file_name = "vocabulary_tech"
    input_file_extension = ".md"
    input_file_path = os.path.join(files_folder_root, files_folder_path, input_file_name + input_file_extension)

    input_file = open_file(filepath=input_file_path)
    input_file_content_splitted = split_clean(content=input_file, delimiter="-----")
    
    input_file_content_transformed = []
    
    # transform input file content into a list of dictionaries
    # each dictionary contains 'term' and 'explanation' keys
    for item in input_file_content_splitted:        
        parts = split_clean(content=item, delimiter="==")
        item_dict = {"term": parts[0].strip(), "explanation": parts[1].strip() if len(parts) > 1 else ""}
        input_file_content_transformed.append(item_dict)

    wf.log_msg(msg={"title": f"Input file tranformed ({len(input_file_content_transformed)} items)", "body": str(input_file_content_transformed)})

    # Process each term and explanation
    final_content = []

    for item in input_file_content_transformed:  # Limit to first 5 items for performance
        term = item["term"]
        explanation = item.get("explanation", None)
        if not explanation:
            # If no explanation, fetch it using the LLM
            llm_explanation = fetch_llm(model_name=model, input=explain_swe_terms(input=term)).get("data", {}).get("content", "")
            wf.log_msg(msg={"title": f"Fetched explanation for term '{term}'", "body": str(llm_explanation)})
            item["explanation"] = llm_explanation
    
    # Transform the list of dictionaries into the required string format
    final_content = [
        f"{item['term']} == {item['explanation']}" if item.get('explanation') else f"{item['term']}"
        for item in input_file_content_transformed
    ]
    final_mixed_content = "\n-----\n".join(final_content)

    wf.log_msg(msg={"title": "Final mixed content", "body": str(input_file_content_transformed)}) 

    # Fix: Don't join final_mixed_content again, it's already a string
    save_result = save_to_external_file2(
        external_root_path=APP_SETTINGS.EXTERNAL_STORAGE_1_LOCAL_PATH,
        filepath=str(Path(files_folder_path) / (input_file_name + "3" + input_file_extension)),
        content=final_mixed_content,  # Use directly, no additional join needed
        delimiter="-----",
        prepend=False            
    )
    wf.log_msg(msg=save_result["message"])
    
    return wf.success_response(
        data=final_mixed_content
    )