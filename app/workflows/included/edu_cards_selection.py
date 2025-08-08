from app.workflows import workflow, Workflow


@workflow()
def edu_cards_selection(task_id):
    """Processes a text file by splitting its content."""
    from app.tools import open_file, split_clean, save_to_external_file2, formatted_datetime
    from app.configs.app_config import APP_SETTINGS
    import os
    import random

    wf = Workflow(task_id=task_id)    

    files_folder_root = APP_SETTINGS.EXTERNAL_STORAGE_1_LOCAL_PATH
    files_folder_path = "_knowledge_base"
    
    # Define files and their desired item counts
    files_to_process = {
        "manual.md": 3,
        "citim_se_dobre.md": 4,
        "povedlo_se.md": 3,
        "afirmace.md": 4,
        "aktivity.md": 2,
        "_for_textio/efektivita.md": 1,
        "laskavost.md": 2,
        "_for_textio/reakce.md": 1,
        "reakce.md": 1
    }

    all_files_content = []
    final_mixed_content = []

    for file_name, items_count in files_to_process.items():
        file_path = os.path.join(files_folder_root, files_folder_path, file_name)
        file_content = open_file(filepath=file_path)
        file_content_splitted = split_clean(content=file_content, delimiter="-----")
        
        # Calculate how many items to pick (min between available items and desired count)
        items_to_pick = min(items_count, len(file_content_splitted))
        selected_items = random.sample(file_content_splitted, items_to_pick)
        
        wf.log_msg(msgTitle="File splitted", msgBody=f"Selected {items_to_pick} items from {len(file_content_splitted)} available")
        all_files_content.append({file_name: selected_items})
        final_mixed_content.extend(selected_items)
        
        
    wf.log_msg(msgTitle=f"Files opened and content splitted: ", msgBody=str(all_files_content))   

    save_result = save_to_external_file2(
            external_root_path=APP_SETTINGS.EXTERNAL_STORAGE_1_LOCAL_PATH,
            filepath=f"_knowledge_base/_for_textio/mixed_cards_{formatted_datetime("%Y%m%d_%H%M%S")}.txt",
            content="\n-----\n".join(final_mixed_content),
            delimiter="-----",
            prepend=False            
        )
    wf.log_msg(msg=save_result["message"])

    return wf.success_response(
        data=all_files_content
    )