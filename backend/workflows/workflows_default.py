from workflows.registry import workflow
from assistants.assistants_default import *
from tools.tools_default import save_to_file, download_news_newsapi, json_db_add_entry, current_datetime_iso, generate_id, user_files_folder_path
from configs.app_config import APP_SETTINGS
import json

# ----------------------
# Workflow functions

@workflow()
def workflow_translation_cs_en_json(input, model=None):
    """Translates text between Czech and English and outputs it in JSON format."""
    if input is None or input.strip() == "":
        return "No input provided." 
    translation_str = assistant_translator_cs_en_json(input=input.strip(), model=model, structured_output=True)
    if not translation_str or not translation_str.get("message", {}).get("content"):
        return "no translation generated"
    translation_str = translation_str.get("message", {}).get("content", "").strip()
    try:
        file_name = "vocabulary"
        translation_parsed = json.loads(translation_str)
        if not isinstance(translation_parsed, dict):
          return "invalid JSON structure"
        translation_str = json.dumps(translation_parsed, indent=2, ensure_ascii=False)
        save_to_file(user_files_folder_path(f"{file_name}.md"), translation_str + "\n\n-----\n", prepend=True)
        json_db_add_entry(db_filepath=user_files_folder_path(f"databases/{file_name}.json"), collection="entries", entry=translation_parsed, add_createdat=True)
        return translation_str
    except json.JSONDecodeError:
        return "failed to decode JSON"


@workflow()
def workflow_translation_cs_en_yaml(input, model=None):
    """Translates text between Czech and English in YAML format."""
    if input is None or input.strip() == "":
        return "No input provided." 
    translation = assistant_translator_cs_en_yaml(input=input, model=model)
    if translation:
        translation = translation["message"]["content"].strip()
        save_to_file(user_files_folder_path("vocabulary_yaml.txt"), translation + "\n\n-----\n", prepend=True)
    return translation


@workflow()
def workflow_translation_cs_en(input, model=None):
    """Translates text between Czech and English."""
    if input is None:
        return None 
    translation = assistant_translator_cs_en(input=input, model=model)
    if translation:
        translation = translation["message"]["content"].strip()
        save_to_file(user_files_folder_path("translations.txt"), translation + "\n\n-----\n", prepend=True)
    return translation


@workflow()
def workflow_text_summarization(input, model=None):
    """Summarizes input text."""
    if input is None:
        return None 
    summarization = assistant_summarize_text(input=input, model=model)
    if summarization:
        summarization = summarization["message"]["content"].strip()
        save_to_file(user_files_folder_path("summaries.txt"), summarization + "\n\n-----\n", prepend=True)
    return summarization


@workflow()
def workflow_situation_analysis(input, model=None):
    """Analyzes a given situation and provides insights."""
    if input is None:
        return None 
    analysis = assistant_analyze_situation(input=input, model=model)
    if analysis:
        analysis = analysis["message"]["content"].strip()
        save_to_file(user_files_folder_path("situace.txt"), analysis + "\n\n-----\n", prepend=True)
    return analysis


@workflow()
def workflow_video_transcript_summarization(input, model=None):
    """Summarizes the transcript of a video."""
    if input is None:
        return None 
    summarization = assistant_summarize_video_transcript(input=input, model=model)
    if summarization:
        summarization = summarization["message"]["content"].strip()
        save_to_file(user_files_folder_path("video_transcript_summaries.txt"), summarization + "\n\n-----\n", prepend=True)
    return summarization


@workflow()
def workflow_explain_simply_lexicon(input, model=None):
    """Provides simple explanations, synonyms, and examples for a given phrase."""
    if input is None:
        return None 
    lexicon = assistant_explain_simply_lexicon(input=input, model=model)
    if lexicon:
        lexicon = lexicon["message"]["content"].strip()
        save_to_file(user_files_folder_path("lexicon.txt"), lexicon + "\n\n-----\n", prepend=True)        
    return lexicon


@workflow()
def workflow_create_assistatnt_prompt(input, model=None):
    """Creates a new assistant based on the input."""
    if input is None:
        return None 
    assistant = assistant_assistant_instructions_creator(input=input, model=model)
    if assistant:
        assistant = assistant["message"]["content"].strip()
        save_to_file(user_files_folder_path("assistants.txt"), assistant + "\n\n-----\n", prepend=True)
    return assistant


@workflow()
def workflow_take_quick_note(input, model=None):
    """Takes a quick note and saves it to both JSON database and file."""
    if input is None:
        return None 
    note = input.strip()
    db_entry = {
        "content": note
    }
    json_db_add_entry(db_filepath=user_files_folder_path("databases/quick_notes.json"), collection="notes", entry=db_entry)
    save_to_file(user_files_folder_path("quick_notes.md"), note + "\n\n-----\n", prepend=True)
    #save_to_external_file("quick_notes_2025_H1_test.md", input.strip() + "\n\n-----\n", prepend=True)    
    return note


@workflow()
def workflow_download_ai_news():
    """Downloads and saves recent AI-related news articles."""
    news = download_news_newsapi(query="openai OR mistral OR claude", lastDays=5, domains="techcrunch.com,thenextweb.com")
    if not news or not news.get("articles"):
        return "no news found"
    file_name = "news"
    articles = news.get("articles", [])
    for article in articles:
        json_db_add_entry(db_filepath=user_files_folder_path(f"databases/{file_name}.json"), collection="entries", entry=article, add_createdat=False)
        save_to_file(user_files_folder_path(f"{file_name}.md"), json.dumps(article, indent=2, ensure_ascii=False) + "\n\n-----\n", prepend=True)    
    return json.dumps(articles, indent=2, ensure_ascii=False)


@workflow()
def workflow_quiz_from_text(input, model=None):	
    """
    Processes a text input and generates quiz questions with answers in json format.    
    """
    if input is None:   
      return "no input provided"
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

    questions = assistant_universal_no_instructions(input=instructions_questions, model="gpt-4o")
    if not questions or not questions.get("message", {}).get("content"):
        return "no questions generated"
    questions = questions.get("message", {}).get("content", "").strip()
    save_to_file(user_files_folder_path("questions.txt"), questions + "\n\n-----\n", prepend=True)  
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
    quiz_questions = assistant_universal_no_instructions(input=instructions_quiz_questions, model="gpt-4o")
    if not quiz_questions:
        return "no quiz questions generated"
    quiz_questions = quiz_questions.get("message", {}).get("content", "").strip()
    save_to_file(user_files_folder_path("quizzes.txt"), quiz_questions + "\n\n-----\n", prepend=True)
    return quiz_questions
    

@workflow()
def workflow_exctract_theses(input, model=None):
    """Exctracts all theses from the input text and saves output to the persistant memory."""
    if input is None:
        return "No input provided." 
    source_text = input.strip()
    instructions_theses = f"""Analyzuj zdrojový text a extrahuj všechny tvrzení (teze) ze zdrojového textu a vypiš je ve strukturovaných bodech. Teze jsou krátké výroky, které shrnují hlavní myšlenku nebo obsah textu. Zajisti úplnost extrakce bez vynechání jakékoli teze. Zachovej původní význam, důležité informace a přesnost formulací. Používej samostatné teze tzn. rozděl složené teze na jednotlivé samostatné teze. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

    Vstupní text:
    {source_text}

    Výstup:
    - [teze 1]
    - [teze 2]
    - [teze 3]
    """
    theses = assistant_universal_no_instructions(input=instructions_theses, model="gpt-4o")
    if not theses or not theses.get("message", {}).get("content"):
        return "no tezis generated"
    theses = theses.get("message", {}).get("content", "").strip()
    save_to_file(user_files_folder_path("theses.txt"), theses + "\n\n-----\n", prepend=True) 
    return theses


@workflow()
def workflow_write_story(input, model=None):
    """Generates short feel-good stories."""
    if input is None:
        return None 
    story = assistant_writer(input=input, model=model)
    if story:
        story = story["message"]["content"].strip()
        save_to_file(user_files_folder_path("stories.md"), story + "\n\n-----\n", prepend=True)
        json_db_add_entry(db_filepath=user_files_folder_path("databases/stories.json"), collection="entries", entry={"input": input.strip(), "content": story}, add_createdat=True)
    return story


@workflow()
def workflow_write_story_reviewed(input, model=None):
    """Generates short feel-good stories reviewed by ai-editor."""
    if input is None:
        return "No input provided." 
    story = assistant_writer(input=input, model=model).get("message", {}).get("content", "").strip()
    if not story:
        return "no story generated"
    instructions_editor = f"""Jseš profesionální editor povídek, který posuzuje povídky a poskytuje zpětnou vazbu k jejich úpravě a zlepšení. Analyzuj vstupní text povídky a její slabé stránky a napiš jasné a stručné doporučení jak text upravit tak aby se odstranily tyto slabé stránky. Doporučení piš formou odrážek v neformátovaném plain text formátu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

    Vstupní text:
    {story}
    """
    editor_feedback = assistant_universal_no_instructions(input=instructions_editor, model="gpt-4o").get("message", {}).get("content")
    if not editor_feedback:
        return "no editor's review generated"
    instructions_edit_story = f"""
    Jseš spisovatel povídek. Tvým úkolem je upravit původní text povídky přesně podle všech instrukcí k úpravě textu a vytvořit tak novou verzi povídky, ve které budou odstraněny slabé stránky a byla zlepšena kvalita textu. Nepřidávej žádné komentáře ani fráze, ani na začátek, ani na konec tvé odpovědi.

    Původní text:
    {story}

    Instrukce k úpravě textu:
    {editor_feedback}
    """
    writer_edited_story = assistant_universal_no_instructions(input=instructions_edit_story, model="gpt-4o").get("message", {}).get("content")
    db_entry = {
        "input": input.strip(),
        "content_for_editor": story.strip(),
        "editor_feedback": editor_feedback.strip(),
        "content": writer_edited_story.strip()        
    }
    save_to_file(user_files_folder_path("stories.md"), writer_edited_story + "\n\n-----\n", prepend=True)
    json_db_add_entry(db_filepath=user_files_folder_path("databases/stories.json"), collection="entries", entry=db_entry, add_createdat=True)
    return writer_edited_story


@workflow()
def workflow_logbook_entry(input, model=None):
    """Writes a logbook entry."""
    if input is None:
        return "No input provided." 
    source_text = input.strip()
    instructions = f"""Na základě zadaného vstupu (může jít o větu, poznámku nebo kus kódu) vytvoř výstup ve strukturovaném JSON formátu se třemi klíčovými poli:
    - "summary": Shrň, co daný úkol nebo kód dělá z pohledu uživatele (co mu to přinese nebo umožní). Pokud se jedná o kód, na začátek věty dej "Kód který, " (např. "Kód, který převede YAML na JSON").
    - "procedure": V bodech popiš, co se děje krok za krokem. Každý bod formuluj jednoduše tak, aby mu rozuměl i netechnický čtenář. Za popis připoj do závorky krátké technické vysvětlení nebo zmínku o použitých funkcích, pokud to dává smysl. Pokud se jedná o kód, je preferované uvést do závorku funkci či metodu. Tam kde to dává smysl, např. pokud se jedná o kód, použij infinitivní slovesa bez podmětu (např. "Vybrat nejvhodnější výsledek ...", "Stáhnout obsah z ..." atd.). 
    - "key_words": Vyjmenuj nejdůležitější použité technologie, knihovny, metody nebo klíčové pojmy. Vypisuj pouze ty, které vystihují účel a průběh úkolu nebo kódu.

    Použij výstupní formát JSON, např.:
    {{
      "summary": "...",
      "procedure": [
        "...",
        "..."
      ],
      "key_words": [
        "...",
        "..."
      ]
    }}

    Vstup:
    {source_text}

    Priklady:
    Priklad vstupu:
    import json
    data = {{"name": "Alice", "age": 30}}
    json_string = json.dumps(data)
    print(json_string)

    Priklad vystupu:
    {{
      "summary": "Kód, který převede slovník s údaji o osobě na JSON řetězec a zobrazí ho.",
      "procedure": [
        "Načíst knihovnu pro práci s JSON formátem (import json).",
        "Vytvořit slovník s informacemi o osobě, jako je jméno a věk (data = {{...}}).",
        "Převést slovník na textový formát JSON (json.dumps()).",
        "Vypsat výsledný JSON řetězec do konzole (print())."
      ],
      "key_words": [
        "Python",
        "json.dumps()",
        "slovník",
        "JSON"
      ]
    }}
    """
    ai_response = assistant_universal_no_instructions(input=instructions, model="gpt-4o", structured_output=True)
    if not ai_response or not ai_response.get("message", {}).get("content"):
        return "no response generated"
    entry = ai_response.get("message", {}).get("content", "").strip()
    try:
        entry_parsed = json.loads(entry)
        if not isinstance(entry_parsed, dict):
            return "invalid JSON structure"            
        # Save pretty-printed JSON to file
        entry_str = json.dumps(entry_parsed, indent=2, ensure_ascii=False)
        save_to_file(user_files_folder_path("logbook.md"), entry_str + "\n\n-----\n", prepend=True)        
        # Save parsed dictionary directly to database
        json_db_add_entry(
            db_filepath=user_files_folder_path("databases/logbook.json"), 
            collection="entries", 
            entry=entry_parsed,  # Use the parsed dict instead of JSON string
            add_createdat=True
        )        
        return entry_str
    except json.JSONDecodeError:
        return "failed to decode JSON"
    


# ----------------------
# Registry of workflows - Extract all workflows dynamically
import inspect
WORKFLOWS_REGISTRY = {
    func.id: {
      'name': func.name, 
      'description': func.description, 
      'function': func, 
      'model': func.model, 
      'category': func.category,
      'type': "workflow",
      'input_required': any(param.name == 'input' and param.default == param.empty 
                          for param in inspect.signature(func).parameters.values()),
      'module': func.__module__
    }
    for name, func in inspect.getmembers(__import__(__name__), inspect.isfunction)
    if hasattr(func, 'id') and hasattr(func, 'is_workflow')  # Check for workflow marker
}
