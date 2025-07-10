from app.workflows.core import *
from app.tools.public import save_to_file, user_files_folder_path, generate_id, current_datetime_iso
from app.assistants.public import assistant_universal_no_instructions

@workflow()
def quiz_from_text(input, model=None):	
    """
    Processes a text input and generates quiz questions with answers in json format.    
    """
    try:
        wf = Workflow()
        
        source_text = input.strip()
        instructions_questions = f"""Na základě zdrojového textu napiš otázky, které se ptají na podstatné informace uvedené ve zdrojovém textu. Přidej ke každé otázce také stručnou odpověď. Pravidla: 
        Na každou otázku bude vždy pouze jedna jednoznačná správná odpověď. 
        Používej samostatné otázky tzn. rozděl složené otázky na jednotlivé samostatné otázky, aby nebylo nutné odpovídat na více věcí najednou.

        <output_format>
        - [otázka 1] ([odpověď na otázku 1])
        - [otázka 2] ([odpověď na otázku 2])
        - [otázka 3] ([odpověď na otázku 3])
        ...
        </output_format>

        <example>
        Zdroj: Nejdelší řeka ČR je Vltava. Nejvýznamnější přítoky řeky Vltavy jsou Berounka a Sázava. Vltava se vlévá do řeky Labe ve městě Mělník.

        Otázky:
        - Jaké je nejdelší řeka v ČR? (Vltava)
        - Jaké jsou nejvýznamnější přítoky Vltavy? (Berounka a Sázava)
        - Do jaké řeky se vlévá Vltava? (Labe)
        - Ve kterém městě se nachází soutok Vltavy a Labe? (Mělník)
        </example>

        Zdrojový text:
        {source_text}
        """

        questions = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_questions, model="gpt-4o"))

        questions_file_path = user_files_folder_path("questions.txt")
        save_to_file(questions_file_path, questions + "\n\n-----\n", prepend=True)        
        wf.add_to_func_log(msgTitle="Quiz questions generated", msgBody=f"Questions saved to {questions_file_path}")

        instructions_quiz_questions = f"""
        Zdrojový text:
        {source_text}

        Otázky:
        {questions}

        Otázky byly vygenerovány na základě zdrojového textu. Pokud je některá otázka nejasná nebo chybná, uprav ji tak, aby byla správná a jednoznačná. 
        Dále ke každé otázce přidej dvě další možnosti odpovědí, které budou nesprávné.

        Výstup vypiš dle šablony výstupu a nepřidávej žádné další texty, fráze, nebo komentáře.
        
        Šablona výstupu:
        {{
        "id": {generate_id(6)},
        "name": "<quiz title>",
        "created": {current_datetime_iso()},
        "tags": ["<topic in one word>"],
        "questions": [
            {{
            "question": "<question 1 title>",
            "options": ["<option 1>", "<option 2>", "<option 3>"],
            "answer": <index of one option from options array representing correct answer>
            }},
            {{
            "question": "<question X title>",
            "options": ["<option 1>", "<option 2>", "<option 3>"],
            "answer": <index of one option from options array representing correct answer>
            }}
        ]
        }}
        """
        quiz_questions = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_quiz_questions, model="gpt-4o"))
        save_to_file(user_files_folder_path("quizzes.txt"), quiz_questions + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=quiz_questions,
            msgBody=f"Quiz questions saved to {user_files_folder_path('quizzes.txt')}"
        )
    except Exception as e:
        return wf.error_response(error=e)