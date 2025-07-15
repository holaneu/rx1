# ----------------------
# playground:
# ----------------------   

from app.tools.included import *


def testing_registries():
    from app.workflows.core import WORKFLOWS_REGISTRY
    print("WORKFLOWS_REGISTRY")
    print(WORKFLOWS_REGISTRY)

    print("WORKFLOWS_REGISTRY without functions")
    workflows_without_functions = {
        name: {k: v for k, v in workflow.items() if k != 'function'}
        for name, workflow in WORKFLOWS_REGISTRY.items()
    }
    print(json.dumps(workflows_without_functions, indent=2))
  
def testing_modular_workflows():
    from app.workflows.core import WORKFLOWS_REGISTRY
    """
    print("Testing modular workflows:")
    for name, workflow in WORKFLOWS_REGISTRY2.items():
        print(f"Workflow: {name}")
        print(f"  Description: {workflow['description']}")
        print(f"  Category: {workflow['category']}")
        print(f"  Input Required: {workflow['input_required']}")
        print(f"  Module: {workflow['module']}")
        print(f"  Function ID: {workflow['function'].id if 'function' in workflow else 'N/A'}")
        print()
    """
    print("WORKFLOWS_REGISTRY without functions")
    workflows_without_functions = {
        name: {k: v for k, v in workflow.items() if k != 'function'}
        for name, workflow in WORKFLOWS_REGISTRY.items()
    }
    print(json.dumps(workflows_without_functions, indent=2))



def testing1():
  print('\nopenai:\n', fetch_llm("gpt-4o-mini", "What is the capital of France?"))
  print('\nmistral:\n', fetch_llm("mistral-small-latest", "What is the capital of France?"))
  print('\ngemini:\n', fetch_llm("gemini-2.0-flash", "What is the capital of France?"))


def testing2():
  from app.assistants.core import ASSISTANTS_REGISTRY
  from app.workflows.core import WORKFLOWS_REGISTRY
  save_to_file(content=fetch_llm(input="what is the capital of Czechia? Write only the name and nothing else", model="mistral-small-latest"), filepath="test/test.txt")
  print(ASSISTANTS_REGISTRY['assistant_translator_cs_en_yaml']['function'](input="namazat si chleba"))
  WORKFLOWS_REGISTRY['workflow_translation_cs_en_yaml']['function'](input="interrogate", model="gemini-2.0-flash-exp")


def testing_registries():
  from app.workflows.core import WORKFLOWS_REGISTRY
  from app.assistants.core import ASSISTANTS_REGISTRY
  from app.tools.core import TOOLS_REGISTRY

  print("ASSISTANTS_REGISTRY")
  print(ASSISTANTS_REGISTRY)

  print("WORKFLOWS_REGISTRY")
  print(WORKFLOWS_REGISTRY)

  print("TOOLS_REGISTRY")
  tools_without_functions = {
    name: {k: v for k, v in tool.items() if k != 'function'}
    for name, tool in TOOLS_REGISTRY.items()
  }
  print(json.dumps(tools_without_functions, indent=2))


def testing20250317():
  base_url=os.getenv('CRAWLER_BASE_URL_1')
  urls = crawl_website_for_urls(
    start_url=f"{base_url}/rubrika/all/",
    url_pattern=f"{base_url}/rubrika/all/",
    max_pages=1000
  )
  print(f"\n *** urls: \n {urls} \n\n")
  specific_urls = extract_urls_from_pages(
      urls=urls,
      css_selector="body main"
  )
  print(f" *** specific_urls: \n {specific_urls} \n\n")
  for url in specific_urls[5:10]:
    parsed_content = download_web_readable_content(url, "body main h1, body main p, body main bloquete")
    url_edited = url.replace(base_url, "").replace("/", "")
    save_to_file(content=parsed_content, filepath=user_data_files_path("downloaded_articles/" + url_edited + ".txt"))
    print(f" *** saved: {url_edited}.txt \n")
  print(" *** DONE *** \n\n")


def testing_github():
  # docs/_posts/2025-02-03-workflows-ideas-2.md
  # docs/_posts/2025-02-03-workflows-ideas.md  
  result = commit_to_github(
      files=["docs/_posts/2025-02-03-workflows-ideas-2.md"],
      commit_message="Add new blog post",
      repo_name="holaneu/auto-posts",
      branch="dev"
  )
  print(result)


def testing20250319():
  #from private.urls_list import urls
  urls = []
  base_url = os.getenv('CRAWLER_BASE_URL_1')
  for url in urls[20:]:
    parsed_content = download_web_readable_content(url, "body main h1, body main p, body main bloquete")
    url_edited = url.replace(base_url, "").replace("/", "")
    save_to_file(content=parsed_content, filepath=user_data_files_path("downloaded_articles/" + url_edited + ".txt"))
    print(f" *** saved: {url_edited}.txt")


def testing20250321():
  dbfile = "outputs/test/databases/quick_notes.json"
  print(json_db_get_entry(db_filepath=dbfile, collection="notes", entry_id="SQ99Ts3BNT"))
  print(json_db_update_entry(db_filepath=dbfile, collection="notes", entry_id="SQ99Ts3BNT", updates={"content": "mazlicek"}))
  # print(json_db_add_entry(db_filepath=dbfile, collection="notes", entry={"content": "prdolka 1"}))
  print(json_db_delete_entry(db_filepath=dbfile, collection="notes", entry_id="0bx7MHfAU0"))


def testing20250326_1():
  message="Write hello in uppercase format."
  print('\n gpt-4o-mini:\n', fetch_llm("gpt-4o-mini", message))
  print('\n gpt-4o:\n', fetch_llm("gpt-4o", message))
  print('\n mistral-small-latest:\n', fetch_llm("mistral-small-latest", message))
  print('\n mistral-large-latest:\n', fetch_llm("mistral-small-latest", message))
  print('\n gemini-2.0-flash:\n', fetch_llm("gemini-2.0-flash", message))
  print('\n gemini-2.0-flash-lite:\n', fetch_llm("gemini-2.0-flash", message))
  print('\n deepseek-chat:\n', fetch_llm("deepseek-chat", message))


def testing20250326_2():
  print(generate_id(10))
  print(current_datetime_iso())
  print(brave_search("openai"))
  print(download_news_newsapi(query="openai OR claude OR deepseek OR mistral", domains="techcrunch.com,thenextweb.com", lastDays=5))


def testing20250326_3():
  from app.assistants.core import ASSISTANTS_REGISTRY
  source = download_web_readable_content("https://www.menicka.cz/4550-bufacek-na-ruzku.html", "#menicka .content .text")
  jidla = ASSISTANTS_REGISTRY['assistant_universal_no_instructions']['function'](input=f"""{source} Jaka jidla jsou dnes v nabidce?""", model="gpt-4o-mini")
  

def testing20250326_4():
  message1="Alice and Bob are going to a science fair on Friday."
  message2="Extract the event information in json format."
  print('\n gpt-4o-mini:\n', fetch_llm("gpt-4o-mini", message1 + " " + message2, structured_output=True))
  print('\n mistral-small-latest:\n', fetch_llm("mistral-small-latest", message1 + " " + message2, structured_output=True))
  print('\n gemini-2.0-flash-lite:\n', fetch_llm("gemini-2.0-flash-lite", message1 + " " + message2, structured_output=True))


def testing20250328():
  print("ocr openai:")
  print(extract_text_from_image_openai(file_path="private/ocr_test/tarotonline_02.png"))
  #print("ocr mistral:")
  #print(extract_text_from_image_mistral_ocr(file_path="private/ocr_test/tarotonline_02.png"))


def testing20250408():
  from app.tools.core import TOOLS_REGISTRY
  tools_without_functions = {
    name: {k: v for k, v in tool.items() if k != 'function'}
    for name, tool in TOOLS_REGISTRY.items()
  }
  def decide_tool_for_task(task):
    instructions = f"""You are manager deciding which tools to use for a specific task.
    Available tools are: 
    {tools_without_functions}
    Your task is to choose the most suitable tool for the task: {task}.
    Use json format for output and include the following fields: tool, reason.
    """
    ai_response = fetch_llm("gemini-2.0-flash", instructions, structured_output=True)
    return ai_response
  
  task1 = "Extract the event information from the text. Use json format for output and include the following fields: event, date, time, location."
  task2 = "Translate the text from Czech to English."
  task3 = "Generate a summary of the text."
  task4 = "Generate id."  
  print(decide_tool_for_task(task3))
  print(decide_tool_for_task(task4))


def testing20250409():
  # step 1: search for restaurants in the area
  query = "obedove menu v blizkem okoli dluhonska 43 v prerove"
  search_results = brave_search(query=query, count=5)
  print(json.dumps(search_results, indent=2), end="\n\n")
  instructions = f"""Your task is to choose the most suitable search result for the origin query: {query}.
    Use json format for output and include the following fields: title, url.
    Search results: 
    {search_results}    
    """
  # step 2: choose the most suitable search result
  selected_search_result = fetch_llm(model="gemini-2.0-flash", input=instructions, structured_output=True)
  print(json.dumps(selected_search_result, indent=2), end="\n\n")
  if not selected_search_result['success']:
    return "somthing went wrong"  
  try:
    # step 3: parse the selected search result
    parsed_result = json.loads(selected_search_result.get('message', {}).get('content', ''))
    print(f"Parsed result: {parsed_result}", end="\n\n")
    if parsed_result and len(parsed_result) > 0:
      url = parsed_result[0].get('url', '')
      print(f"Selected URL: {url}", end="\n\n")
      if url:
        # step 4: download the content of the selected search result
        source = download_web_readable_content(url, "#menicka .content .text")
        print(source, end="\n\n")
    else:
      print("No valid URL found in search results")
  except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
  # step 5: extract foods and their origin restaurants from the text
  source_shorten = source[:len(source) // 4]
  source_shorten = source_shorten[100:]
  instructions2 = f"""Your task is to extract foods and its origin restaurants from a text.
    Use json format for output and include the following fields: food, restaurant.
    Text: {source_shorten}
    """
  extracted_foods = fetch_llm(model="gemini-2.0-flash", input=instructions2, structured_output=True)
  print(f"extracted foods: {json.dumps(extracted_foods.get('message', {}).get('content', ''), indent=2)}", end="\n\n")
  # step 6: clean the extracted foods data and print results
  try:
    import re
    cleaned_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', extracted_foods.get('message', {}).get('content', ''))
    json_data = json.loads(cleaned_text)    
    print("extracted foods result:")
    print(json.dumps(json_data, indent=2, ensure_ascii=False), end="\n\n")
  except json.JSONDecodeError as e:
      print(f"Error parsing JSON: {e}")
      # Optional: Print the problematic part of the string
      error_position = e.pos
      context = cleaned_text[max(0, error_position-50):min(len(cleaned_text), error_position+50)]
      print(f"\nContext around error (pos {error_position}):")
      print(context)


def testing20250416():
  """Testing new model gpt-4.1. for deciding which tool to use for a specific task."""
  from app.tools.core import TOOLS_REGISTRY
  tools_without_functions = {
    name: {k: v for k, v in tool.items() if k != 'function'}
    for name, tool in TOOLS_REGISTRY.items()
  }
  def decide_tool_for_task(task):
    instructions = f"""You are manager deciding which tools to use for a specific task.
    Available tools are: 
    {tools_without_functions}
    Your task is to choose the most suitable tool for the task: {task}.
    Use json format for output and include the following fields: tool, reason.
    """
    ai_response = fetch_llm(model="gpt-4.1", input=instructions, structured_output=True)
    return ai_response
  
  task1 = "Extract the event information from the text. Use json format for output and include the following fields: event, date, time, location."
  task2 = "Translate the text from Czech to English."
  task3 = "Generate a summary of the text."
  task4 = "Generate id."  
  print('gpt-4.1 test', 'task3', decide_tool_for_task(task3), sep="\n", end="\n\n")
  print('gpt-4.1 test', 'task4', decide_tool_for_task(task4), sep="\n", end="\n\n")


def testing20250416_2():
  db_path=user_data_files_path("databases/test1.json")
  # create new db without schema
  new_db = json_db_create_db_without_schema(db_filepath=db_path)
  print(f"db: {new_db}", end="\n\n")
  # add new entry to the db
  entry_content = {
    "content": f"test test {current_datetime_iso()}"
  }
  db_entry = json_db_add_entry(db_filepath=db_path, collection="entries", entry=entry_content)
  print(f"db_entry: {db_entry}", end="\n\n")
  # receive entry_id of the newly added entry
  if db_entry.get('success', False):
    db_entry_id = db_entry["data"]["entry_id"]
    print(f"db_entry_id: {db_entry_id}", end="\n\n")
  # load the whole db
  db = json_db_load(db_filepath=db_path)
  print(f"db: {db}", end="\n\n")  
  # get first collection
  db_collection_key = next(iter(db.get('collections', {}).keys()), None)
  print(f"db_collection_name: {db_collection_key}", end="\n\n")
  #db_collection = next(iter(db.get('collections', {}).values()), {})
  db_collection_value = db.get('collections', {}).get(db_collection_key, [])
  print(f"db_collection: {db_collection_value}", end="\n\n")
  # delete the last entry from the db
  last_entry_id = db_collection_value[-1].get('id', None)
  print(f"last_entry_id: {last_entry_id}", end="\n\n")
  removed_entry = json_db_delete_entry(db_filepath=db_path, collection=db_collection_key, entry_id=last_entry_id)
  print(f"removed_entry: {removed_entry}", end="\n\n")
  # update the first entry
  first_entry_id = db_collection_value[0].get('id', None)
  first_entry_content = db_collection_value[0].get('content', None)
  updated_entry_content = first_entry_content + " UPDATED"
  print(f"first_entry_id: {first_entry_id}", f"first_entry_content: {first_entry_content}", sep="\n", end="\n\n")
  updated_entry = json_db_update_entry(db_filepath=db_path, collection=db_collection_key, entry_id=first_entry_id, updates={"content": updated_entry_content})
  print(f"updated_entry: {updated_entry}", end="\n\n")
  # get collection by collection key
  collection = json_db_get_collection(db_filepath=db_path, collection=db_collection_key).get('data', []).get('entries', [])
  print(f"collection: {collection}", end="\n\n")
  

def testingCreateNewDbs():
  # create new dbs
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/vocabulary.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/logbook.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/questions.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/lexicon.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/news.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/stories.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/situations.json"), initial_collections=["entries"])
  json_db_create_db_without_schema(db_filepath=user_data_files_path("databases/blog_posts.json"), initial_collections=["entries"])


def testingConvertTxtToDb_logbook():
  #json_db_delete_entry(db_filepath=user_data_files_path("databases/logbook.json"), collection="entries", entry_id="JDmKAZcnry")
  data_file = open_file(filepath=user_data_files_path("logbook.md"))
  data_parsed = [json.loads(d.strip()) for d in data_file.split("-----") if d.strip()]
  print(f"data: {json.dumps(data_parsed, indent=2, ensure_ascii=False)}", end="\n\n")
  for item in reversed(data_parsed):
    json_db_add_entry(db_filepath=user_data_files_path("databases/logbook.json"), collection="entries", entry=item, add_createdat=True)


def testingConvertTxtToDb_vocabulary():
  file_name = "vocabulary"
  data_file = open_file(filepath=user_data_files_path(f"{file_name}.md"))
  data_parsed = [json.loads(d.strip()) for d in data_file.split("-----") if d.strip()]
  start_index = 0
  end_index = len(data_parsed)
  data_fragment = data_parsed[start_index:end_index]
  print(f"data: {json.dumps(data_fragment, indent=2, ensure_ascii=False)}", end="\n\n")
  for item in reversed(data_fragment):
    json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=item, add_createdat=True)


def testingConvertTxtToDb_stories():
  file_name = "stories"
  data_item_format = "text"
  data_file = open_file(filepath=user_data_files_path(f"{file_name}.md"))
  data_parsed = [d.strip() for d in data_file.split("-----") if d.strip()]
  start_index = 0
  end_index = len(data_parsed)
  data_fragment = data_parsed[start_index:end_index]
  for item in reversed(data_fragment):
    if data_item_format == "json":
      item = json.loads(item.strip())
    elif data_item_format == "text":
      item = {
        "content": item.strip()
      }
    print(f"{json.dumps(item, indent=2, ensure_ascii=False)}", end="\n\n")
    json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=item, add_createdat=True)
  

def testingConvertTxtToDb_news():
  file_name = "news"
  data_item_format = "json"
  data_file = open_file(filepath=user_data_files_path(f"{file_name}.md"))
  data_parsed = [d.strip() for d in data_file.split("-----") if d.strip()]
  start_index = 0
  end_index = len(data_parsed)
  data_fragment = data_parsed[start_index:end_index]
  news_all = []
  for item in reversed(data_fragment):
    if data_item_format == "json":
      item = json.loads(item.strip())
    elif data_item_format == "text":
      item = {
        "content": item.strip()
      }
    articles = item.get("articles", [])
    news_all.extend(articles)
    #print(f"{json.dumps(articles, indent=2, ensure_ascii=False)}", end="\n\n")
    #json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=item, add_createdat=True)
  #print(f"{json.dumps(news_all, indent=2, ensure_ascii=False)}", end="\n\n")
  print(len(news_all))
  news_all_text_version = "\n\n-----\n\n".join([json.dumps(article, indent=2, ensure_ascii=False) for article in news_all])
  save_to_file(content=news_all_text_version, filepath=user_data_files_path(f"databases/{file_name}.md"), prepend=True)
  """for article in news_all:
    json_db_add_entry(db_filepath=user_data_files_path(f"databases/{file_name}.json"), collection="entries", entry=article, add_createdat=False)"""


def testingExportToolsRegistry():
  from app.tools.core import TOOLS_REGISTRY
  print("TOOLS_REGISTRY without functions")
  tools = {
    name: {k: v for k, v in tool.items() if k != 'function'}
    for name, tool in TOOLS_REGISTRY.items()
  }
  tools_str = json.dumps(tools, indent=2, ensure_ascii=False)
  print(tools_str)
  save_to_file(content=tools_str + "\n\n-----\n\n", filepath=user_data_files_path(f"tools_registry.json"), prepend=True)


def testingImportUserWf():
    """Testing import of user workflow from custom_workflows directory."""
    import app.workflows
    from app.workflows.core import WORKFLOWS_REGISTRY

    print("WORKFLOWS_REGISTRY without functions")
    workflows_without_functions = {
        name: {k: v for k, v in workflow.items() if k != 'function'}
        for name, workflow in WORKFLOWS_REGISTRY.items()
    }
    print(json.dumps(workflows_without_functions, indent=2))


# ----------------------
# run test function(s):
# ---------------------- 

#testingExportToolsRegistry()
#testing_registries()
#testingImportUserWf()
testingExportToolsRegistry()
