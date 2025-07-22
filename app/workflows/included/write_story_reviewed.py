from app.workflows.core import workflow, Workflow
from app.tools.included import save_to_file, user_data_files_path, json_db_add_entry
from app.assistants.included import assistant_writer, assistant_universal_no_instructions

@workflow()
def write_story_reviewed(input, task_id, model="openai/gpt-4.1"):
    """Generates short feel-good stories reviewed by ai-editor."""
    try:
        wf = Workflow(task_id=task_id)
        # step 1: Generate the story
        story = wf.get_assistant_output_or_raise(assistant_writer(input=input.strip(), model=model))

        wf.add_msg_to_log(msgTitle="LLM: Story generated", msgBody=story)

        # step 2: Get feedback from the editor
        instructions_editor = f"""Jseš profesionální editor povídek, který posuzuje povídky a poskytuje zpětnou vazbu k jejich úpravě a zlepšení. Analyzuj vstupní text povídky a její slabé stránky a napiš jasné a stručné doporučení jak text upravit tak aby se odstranily tyto slabé stránky. Doporučení piš formou odrážek v neformátovaném plain text formátu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

        Vstupní text:
        {story}
        """

        editor_feedback = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_editor, model=model))

        wf.add_msg_to_log(msgTitle="LLM: Editor feedback generated", msgBody=editor_feedback)
        
        # step 3: Edit the story based on the feedback
        instructions_edit_story = f"""
        Jseš spisovatel povídek. Tvým úkolem je upravit původní text povídky přesně podle všech instrukcí k úpravě textu a vytvořit tak novou verzi povídky, ve které budou odstraněny slabé stránky a byla zlepšena kvalita textu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

        Původní text:
        {story}

        Instrukce k úpravě textu:
        {editor_feedback}
        """
        writer_edited_story = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_edit_story, model=model))
        wf.add_msg_to_log(msgTitle="LLM: Edited story generated", msgBody=writer_edited_story)

        # step 4: Save the story and feedback to file and database
        db_entry = {
            "input": input.strip(),
            "content_for_editor": story.strip(),
            "editor_feedback": editor_feedback.strip(),
            "content": writer_edited_story.strip()        
        }

        user_input1_form = [
            #{"type": "text", "name": "user_name", "label": "What is your name?", "placeholder": "e.g., Jane Doe", "required": True},
            {"type": "select", "name": "save-confirm", "label": "Do you want to save it?", "options": ["Yes", "No"], "required": True}
        ]
        user_input1 = yield wf.interaction_request(
            msgTitle="Confirmation required",
            msgBody="Do you want to save the result to file?",
            form_elements=user_input1_form
        )

        if user_input1.get("save-confirm") != "Yes":
            return wf.success_response(
                data={"edited_story": writer_edited_story},
                msgBody="Note: Result not saved to file."
            )

        # Save to file
        save_file_result = save_to_file(filepath=user_data_files_path("stories_reviewed.md"), content=db_entry, delimiter="-----", prepend=True)
        wf.add_msg_to_log(msg=save_file_result["message"])

        #save_db_result = json_db_add_entry(db_filepath=user_data_files_path("databases/stories.json"), collection="entries", entry=db_entry, add_createdat=True)
        #wf.add_msg_to_log(msg=save_db_result["message"])

        return wf.success_response(
            data={"edited_story": writer_edited_story},
            msgBody="Result saved to file."
        )

    except Exception as e:
        return wf.error_response(error=e)