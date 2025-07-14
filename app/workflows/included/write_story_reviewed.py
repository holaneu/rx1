from app.workflows.core import workflow, Workflow
from app.tools.included import save_to_file, user_data_files_path, json_db_add_entry
from app.assistants.included import assistant_writer, assistant_universal_no_instructions

@workflow()
def write_story_reviewed(input, model=None):
    """Generates short feel-good stories reviewed by ai-editor."""
    try:
        wf = Workflow()
        # step 1: Generate the story
        story = wf.get_assistant_output_or_raise(assistant_writer(input=input.strip(), model=model))
        wf.add_to_func_log(msgTitle="Story generated", msgBody=story)
        # step 2: Get feedback from the editor
        instructions_editor = f"""Jseš profesionální editor povídek, který posuzuje povídky a poskytuje zpětnou vazbu k jejich úpravě a zlepšení. Analyzuj vstupní text povídky a její slabé stránky a napiš jasné a stručné doporučení jak text upravit tak aby se odstranily tyto slabé stránky. Doporučení piš formou odrážek v neformátovaném plain text formátu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

        Vstupní text:
        {story}
        """
        editor_feedback = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_editor, model="gpt-4o"))
        wf.add_to_func_log(msgTitle="Editor feedback received", msgBody=editor_feedback)
        # step 3: Edit the story based on the feedback
        instructions_edit_story = f"""
        Jseš spisovatel povídek. Tvým úkolem je upravit původní text povídky přesně podle všech instrukcí k úpravě textu a vytvořit tak novou verzi povídky, ve které budou odstraněny slabé stránky a byla zlepšena kvalita textu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

        Původní text:
        {story}

        Instrukce k úpravě textu:
        {editor_feedback}
        """
        writer_edited_story = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_edit_story, model="gpt-4o"))
        wf.add_to_func_log(msgTitle="Story edited", msgBody=writer_edited_story)
        # step 4: Save the story and feedback to file and database
        db_entry = {
            "input": input.strip(),
            "content_for_editor": story.strip(),
            "editor_feedback": editor_feedback.strip(),
            "content": writer_edited_story.strip()        
        }
        # Save to file
        save_file_result = save_to_file(user_data_files_path("stories.md"), writer_edited_story + "\n\n-----\n", prepend=True)
        wf.add_to_func_log(
            msgTitle=save_file_result["message"]["title"],
            msgBody=save_file_result["message"]["body"]
        )

        json_db_add_entry(db_filepath=user_data_files_path("databases/stories.json"), collection="entries", entry=db_entry, add_createdat=True)
        return wf.success_response(
            data=writer_edited_story,
            msgBody=f"Story reviewed and saved to {user_data_files_path('stories.md')}"
        )

    except Exception as e:
        return wf.error_response(error=e)   