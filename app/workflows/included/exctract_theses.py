from app.workflows.core import workflow, Workflow
from app.assistants.included import assistant_universal_no_instructions
from app.tools.included import save_to_file, user_data_files_path

@workflow()
def exctract_theses(input, model=None):
    """Exctracts all theses from the input text and saves output to the persistant memory."""
    try:
        wf = Workflow()
        source_text = input.strip()
        instructions_theses = f"""Analyzuj zdrojový text a extrahuj všechny tvrzení (teze) ze zdrojového textu a vypiš je ve strukturovaných bodech. Teze jsou krátké výroky, které shrnují hlavní myšlenku nebo obsah textu. Zajisti úplnost extrakce bez vynechání jakékoli teze. Zachovej původní význam, důležité informace a přesnost formulací. Používej samostatné teze tzn. rozděl složené teze na jednotlivé samostatné teze. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

        Vstupní text:
        {source_text}

        Výstup:
        - [teze 1]
        - [teze 2]
        - [teze 3]
        """
        theses = wf.get_assistant_output_or_raise(assistant_universal_no_instructions(input=instructions_theses, model="gpt-4o"))
        


        file_path = user_data_files_path("theses.txt")
        save_file_result = save_to_file(file_path, theses + "\n\n-----\n", prepend=True)
        wf.add_to_func_log(
            msgTitle=save_file_result["message"]["title"],
            msgBody=save_file_result["message"]["body"]
        )
        return wf.success_response(
            data=theses,
            msgBody=f"Theses extracted and saved to {file_path}"
        )
    except Exception as e:
        return wf.error_response(error=e)
