import os
import requests
import json
import re
from pathlib import Path
from typing import Dict, Any

from app.tools.core import tool
from app.configs.ai_config import llm_models, llm_providers
from app.configs.app_config import APP_SETTINGS
from app.utils.response_types import ResponseKey, ResponseStatus


@tool(category='date_time')
def formatted_datetime(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Returns the current date and time formatted as specified.
    Args:
        format (str): The format string for datetime, defaults to "%Y-%m-%d %H:%M:%S"
    Returns:
        str: Current date and time formatted according to the provided format string
    Example:
        >>> formatted_datetime()
        '2025-03-05 11:00:29'
    """
    import datetime
    return datetime.datetime.now().strftime(format)


@tool(category='llm')
def get_llm_model_info(model_name):
    """
    Retrieves an AI model configuration from a list of available models by its name.
    Args:
        model_name (str): The name of the AI model to search for.
    Returns:
        dict or None: The model configuration dictionary if found, None otherwise. 
        The model dictionary contains model parameters and settings.
    """
    for model in llm_models:
        if model['name'] == model_name:
            return model
    return None


@tool(category='llm')
def get_llm_provider_info(provider_name):
    """
    Retrieve information about a specific LLM provider by name.
    Args:
        provider_name (str): The name of the LLM provider to search for.
    Returns:
        dict or None: The provider's information as a dictionary if found, otherwise None.
    """

    for provider in llm_providers:
        if provider['name'] == provider_name:
            return provider
    return None


@tool(category='llm')
def format_str_as_llm_message_obj(input):
    if isinstance(input, str):
        return [{"role": "user", "content": input}]
    return input


@tool()
def fetch_llm(model_name, input, structured_output=None, response_format=None, temperature=0.7):
    """
    Fetches AI response using specified model and input.
    This function processes the input through different AI models based on their API type.
    Currently supports OpenAI and Anthropic API types.
    Args:
        model (str or dict): The AI model identifier or configuration dictionary
        input (str): The input text/prompt to be processed by the AI model
    Returns:
        str or None: The AI model's response if successful, None if the model is not found
        or if the API type is not supported
    Example:
        >>> response = fetch_ai("gpt-4", "What is the capital of France?")
        >>> print(response)
        "The capital of France is Paris."
    """
    model_info = get_llm_model_info(model_name)
    if model_info is None:
        raise Exception(f"Model not found in configuration")
    
    provider_info = get_llm_provider_info(provider_name=model_info['provider'])
    if provider_info is None:
        raise Exception(f"Provider not found in configuration")
    
    provider_api_key = provider_info.get('api_key')
    provider_base_url = provider_info.get('base_url')
    provider_api_type = provider_info.get('api_type')

    if not provider_api_key:
        raise Exception("provider_api_key environment variable is not set")
    
    if provider_api_type == 'openai':
        return call_api_of_type_openai_v3(
            model_name=model_info['name'],
            api_key=provider_api_key,
            base_url=provider_base_url,
            input=input,
            structured_output=structured_output,
            response_format=response_format,
            temperature=temperature #temperature if temperature is not None else 0.7
            )
    return None


@tool()
def call_api_of_type_openai_v3(model_name, api_key, base_url, input, structured_output=None, response_format=None, temperature=None):
  """
  Calls OpenAI API with the given model and input.
  This function sends a request to OpenAI's API, handles the response, logs the interaction,
  and returns the processed result.
  Args:
    model (dict): Dictionary containing model configuration including 'name' key
    input (str or list): Input text or list of message objects to send to the API
    structured_output (bool, optional): If True, forces JSON output format. Defaults to None
    response_format (dict, optional): Custom response format configuration. If None and structured_output is True, defaults to JSON object format. Defaults to None
    temperature (float, optional): Controls randomness in the model's output. Values range from 0 to 2,
    where 0 is more focused/deterministic and higher values produce more random outputs. Defaults to 0.7 if not specified.
  Returns:
    dict or None: If successful, returns a dictionary containing:
      - success (bool): True if API call succeeded
      - origin (str): Name of the calling function
      - message (dict): Response message containing:
        - content (str): The generated text response
        - role (str): Role of the message (e.g. "assistant")
      - info (dict): Additional information including:
        - model (str): Name of the model used
        - prompt_tokens (int): Number of tokens in the prompt
        - completion_tokens (int): Number of tokens in the completion
        - total_tokens (int): Total tokens used
    Returns None if API call fails or encounters an error
  Raises:
    Exception: Catches and logs any exceptions during API call
  Note:
    - Requires valid model configuration with API key and base URL
    - Automatically logs all interactions to a timestamped file
    - Supports JSON mode for structured outputs
    - Uses a default temperature of 0.7 for generation
  """
  import datetime
  #model_info = get_llm_model_info(model_name['name'])
  
  headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
  }

  payload = {
    "model": model_name,
    "messages": format_str_as_llm_message_obj(input),
    "temperature": temperature
  }
  # turn on JSON mode
  if structured_output == True:
    if response_format == None:
      payload["response_format"] = { "type": "json_object" }

  try:
    response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
      result = response.json()
      log_timestamp = formatted_datetime("%Y%m%d_%H%M%S") #datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
      log_filepath = user_data_files_path(f"logs/ai_response_{log_timestamp}.log")
      log_content = {
        "input": format_str_as_llm_message_obj(input),
        "output": result
      }
      log_content = json.dumps(log_content, ensure_ascii=False, indent=2)
      save_to_file(content=log_content, filepath=log_filepath)
      output = {
        "success": True,
        "message": {
          "content": result["choices"][0]["message"]["content"],
          "role": result["choices"][0]["message"]["role"]
        },        
        "info": {
          "model": result["model"],
          "prompt_tokens": result["usage"]["prompt_tokens"],
          "completion_tokens": result["usage"]["completion_tokens"],
          "total_tokens": result["usage"]["total_tokens"]  
        }
      }
      return output
    else:
      raise Exception(f"Error returned by LLM provider: {response.status_code} - {response.text}")
      #print(f"Error: {response.status_code}")
      #print(response.text)
      #return None
  except Exception as e:
    raise Exception(f"Error calling LLM model: {e}")
    #print(f"Error calling model: {e}")
    #return None


@tool()
def assistant_output_formatted(assistant_output):
    """Extracts the message content from an assistant output or raises an error if not found."""
    if not assistant_output or 'message' not in assistant_output:
        raise Exception("Assistant output is empty or does not contain a message.")        
    message = assistant_output['message']
    if 'content' not in message:
        raise Exception("Message does not contain content.")        
    return message['content'].strip()


@tool()
def download_news_newsapi(query=None, lastDays=None, domains=None):
  """
  Fetches news articles from NewsAPI based on configured settings.
  Returns:
    dict: News articles data or None if request fails
  """
  import datetime
  base_url = "https://newsapi.org/v2/everything"
  today = datetime.datetime.now()
  start_date = today - datetime.timedelta(days=lastDays)
  from_date = start_date.strftime("%Y-%m-%d")
  to_date = today.strftime("%Y-%m-%d")

  params = {
    "q": query,
    "searchIn": "title,description",
    "from": from_date,
    "to": to_date,
    "sortBy": "popularity",
    "language": "en",
    "domains": domains,
    "apiKey": os.getenv("NEWSAPI_API_KEY"),
    "pageSize": 20,
    "page": 1
  }

  try:
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
      return response.json()
    else:
      print(f"Error: {response.status_code}")
      print(response.text)
      return None
  except Exception as e:
    print(f"Error calling NewsAPI: {e}")
    return None


@tool()
def open_file(filepath):
  """
  Opens and reads a text file, returning its contents as a string.
  Args:
    filepath (str): The path to the file to be opened and read.
  Returns:
    str: The complete contents of the file as a string.
  Raises:
    FileNotFoundError: If the specified file does not exist.
    IOError: If there is an error reading the file.
  """
  with open(filepath, 'r', encoding='utf-8') as infile:
      return infile.read()


@tool()
def save_to_file(filepath, content, prepend=False, delimiter=None):
  """Saves content to a file with various safety checks and options.
  This function saves the provided content to a file, with options to prepend or append. 
  It includes several safety checks for content validity and file path security.
  Args:
    filepath (str): Relative path where the file should be saved. Path traversal is not allowed.
    content (str or convertible to str): Content to write to the file. Cannot be empty.
    prepend (bool, optional): If True, adds content at the beginning of file. If False, appends to end. 
      Defaults to False.
  Raises:
    ValueError: If content is empty, not convertible to string, contains invalid Unicode,
      exceeds 10MB, or if filepath attempts path traversal.
    IOError: If there are issues with file operations.
    OSError: If there are system-level errors during file operations.
  Notes:
    - Creates directories in the path if they don't exist
    - Adds newline after content
    - Files are written using UTF-8 encoding
    - Maximum file size limit is 10MB
    - Paths are relative to APP_SETTINGS["output_folder"]
  """
  try:
    if content is None:
      raise ValueError("Content cannot be empty")
    if not isinstance(content, str):
      content = str(content)
      if not isinstance(content, str):
        raise ValueError("Content must be a convertible to string")
    if len(content.strip()) == 0:
      raise ValueError("Content cannot be empty")
    if ".." in filepath or filepath.startswith("/"):
      raise ValueError("Invalid filepath: Path traversal not allowed")    
    
    #full_path = os.path.join(APP_SETTINGS["output_folder"], filepath)
    full_path = filepath
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
      os.makedirs(directory)
    
    try:
      content_size = len(content.encode('utf-8'))
    except UnicodeEncodeError:
      raise ValueError("Content contains invalid Unicode characters")
    if content_size > 10 * 1024 * 1024:
      raise ValueError("Content too large: Exceeds 10MB limit")
    
    # Add delimiter if it's a valid non-empty string with at least 1 non-whitespace character
    if isinstance(delimiter, str) and len(delimiter.strip()) >= 1:
        content += f"\n\n{delimiter}\n"

    if prepend:
      # Read existing content if file exists
      existing_content = ''
      if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as infile:
          existing_content = infile.read()
      # Write new content followed by existing content
      with open(full_path, 'w', encoding='utf-8') as outfile:
        outfile.write(content + '\n' + existing_content)
    else:
      # Normal append mode
      with open(full_path, 'a', encoding='utf-8') as outfile:
        outfile.write(content + '\n')
    # Return JSON status after successful save
    return {
      ResponseKey.STATUS: ResponseStatus.SUCCESS,
      ResponseKey.MESSAGE: {
        ResponseKey.TITLE: "File saved",
        ResponseKey.BODY: f"File path: {full_path}"
      }
    }
  except (IOError, OSError) as e:
    print(f"Error writing to file {filepath}: {e}")
    raise
  except Exception as e:
    print(f"Unexpected error while saving file {filepath}: {e}")
    raise

# REMOVE:
@tool()
def save_to_external_file(filename, content, prepend=False, base_path=None):
    """Save content to a file in an external location, creating directories if needed."""
    # Use environment variable if set, otherwise use default path
    base_path = base_path or os.getenv('EXTERNAL_STORAGE_1_LOCAL_PATH')
    base_path = Path(base_path)
    full_path = base_path / filename
    
    # Validate path is outside project directory
    try:
        if not full_path.is_absolute():
            full_path = full_path.resolve()
        if not str(full_path).startswith(str(base_path)):
            raise ValueError("Path must be within the external storage directory")
            
        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'r+' if full_path.exists() else 'w'
        if prepend and full_path.exists():
            existing_content = full_path.read_text(encoding='utf-8')
            full_path.write_text(content + existing_content, encoding='utf-8')
        else:
            write_mode = 'a' if full_path.exists() else 'w'
            with open(full_path, write_mode, encoding='utf-8') as f:
                f.write(content)
        return {
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "File saved",
                ResponseKey.BODY: f"File path: {full_path}"
            }
        }        
    except Exception as e:
        print(f"Error saving to external file: {e}")
        raise


@tool()
def save_to_external_file2(filepath, content, prepend=False, external_root_path=None, delimiter=None):
    """Save content to a file under the given external root path, creating directories if needed.

    If `delimiter` is a non-empty string (min 1 char), append "\n\n<delimiter>\n\n" to the content.
    """
    import os
    from pathlib import Path

    if not external_root_path:
        raise ValueError("external_root_path must be provided")

    external_root_path = Path(external_root_path)
    if not external_root_path.is_absolute():
        external_root_path = external_root_path.resolve()

    # Normalize filepath to ensure it does not override the root path
    filepath = Path(filepath.lstrip("/\\"))
    full_path = external_root_path / filepath

    try:
        # Validate full_path stays within external_root_path
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(external_root_path.resolve())):
            raise ValueError("Path must be within the external storage root directory")

        # Add delimiter if it's a valid non-empty string with at least 1 non-whitespace character
        if isinstance(delimiter, str) and len(delimiter.strip()) >= 1:
            content += f"\n\n{delimiter}\n\n"

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if prepend and full_path.exists():
            existing_content = full_path.read_text(encoding='utf-8')
            full_path.write_text(content + existing_content, encoding='utf-8')
        else:
            write_mode = 'a' if full_path.exists() else 'w'
            with open(full_path, write_mode, encoding='utf-8') as f:
                f.write(content)

        return {
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "File saved",
                ResponseKey.BODY: f"File path: {full_path}"
            }
        }

    except Exception as e:
        print(f"Error saving to external file: {e}")
        raise


@tool()
def save_to_json_file(data, output_file):
    """Saves data to a JSON file with UTF-8 encoding.
    Args:
        data: The data to be saved to the JSON file. Can be any JSON-serializable object.
        output_file (str): The path to the output JSON file.
    Example:
        data = {"name": "John", "age": 30}
        save_to_json_file(data, "output.json")
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "JSON File saved",
                ResponseKey.BODY: f"File path: {output_file}"
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        raise e
    

import re

@tool()
def split_clean(content, delimiter='-----'):
    """
    Splits a string by a delimiter and strips whitespace from each part.
    Removes empty strings from the result.

    Args:
        content (str): The input string to be split and cleaned.
        delimiter (str, optional): The delimiter string to split by. Defaults to '-----'.
            The delimiter is treated as a regex pattern and split occurs on one or more consecutive occurrences.

    Returns:
        list[str]: A list of non-empty strings where:
            - Each string is a part of the original content split by the delimiter
            - Leading and trailing whitespace is removed from each part
            - Empty strings are removed

    Example:
        >>> text = "Hello\\n-----\\nWorld"
        >>> split_clean(text)
        ['Hello', 'World']

        >>> text = "a\\n---\\nb\\n---\\n"
        >>> split_clean(text, delimiter='---')
        ['a', 'b']
    """
    delimiter_pattern = re.escape(delimiter)
    parts = re.split(rf'{delimiter_pattern}+', content.strip())
    cleaned_parts = [part.strip() for part in parts if part.strip()]
    return cleaned_parts


@tool()
def generate_id(length=10):    
  """
  Generate a random ID string of specified length using letters and numbers.  
  Args:
    length (int): Length of ID to generate, defaults to 10    
  Returns:
    str: Random string of specified length containing letters and digits    
  Example:
    >>> generate_id()
    'bK9mP4xL2n'
    >>> generate_id(5)
    'Yw3kP'
  """
  import random
  import string
  chars = string.ascii_letters + string.digits
  return ''.join(random.choice(chars) for _ in range(length))


@tool()
def current_datetime_iso():
    """
    Returns the current datetime in ISO 8601 format.
    Returns:
        str: Current datetime in ISO 8601 format (e.g. "2025-03-05T11:00:29.307714+00:00")
    Example:
        >>> current_datetime_iso()
        '2025-03-05T11:00:29.307714+00:00'
    """
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat()   


@tool()
def user_data_files_path(file_path: str) -> str:
    return os.path.join(APP_SETTINGS.USER_DATA_FILES_PATH, file_path) 


@tool()
def user_data_path(file_path: str) -> str:
    return os.path.join(APP_SETTINGS.USER_DATA_PATH, file_path) 


@tool(category='database')
def json_db_load(db_filepath: str) -> dict:
    """
    Load JSON database from a file.
    
    Args:
        filepath (str): Path to the JSON database file
    Returns:
        dict: Database content or empty dict if file not found
    """
    try:
        with open(db_filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


@tool(category='database')
def json_db_save(db_filepath: str, data: dict) -> dict:
  """
  Save JSON database to a file.
  
  Args:
    db_filepath (str): Path to save the JSON database
    data (dict): Data to save
    
  Returns:
    dict: Response object with success status and message
    Example:
      {"success": True, "message": "Database saved successfully."}
      {"success": False, "message": "Error saving database file: error"}
  """
  try:
    with open(db_filepath, "w", encoding="utf-8") as file:
      json.dump(data, file, indent=2, ensure_ascii=False)
    return {
      "success": True,
      "message": "Database saved successfully."
    }
  except Exception as e:
    return {
      "success": False,
      "message": f"Error saving database file: {str(e)}"
    }


@tool(category='database')
def json_db_create_db_without_schema(
   db_filepath: str, 
   title: str = None, 
   description: str = None, 
   initial_collections: list[str] = None,
   owner: str = None, 
   tags: list[str] = None   
   ) -> dict:
    """
    Create a new JSON database with basic structure and info, without schema validation.

    Args:
      db_filepath (str): Path to save the new database file
      title (str): Title of the database (optional, defaults to filename)
      description (str): Description of the database (optional)
      initial_collections (list): Names of collections to include (optional) 
      owner (str): Owner name (optional)
      tags (list): List of tags (optional)

    Returns:
      dict: Response object with success status and message
      Example:
        {
          "success": True, 
          "message": "Database file created successfully.",
          "data": {
            "db_id": "abc123", 
            "db_path": "path/to/db.json"
          }
        }
        {"success": False, "message": "Database file already exists."}
    """
    # Check if file already exists
    if os.path.exists(db_filepath):
        return {
          "success": False,
          "message": "Database file already exists.",
          "error": {
            "type": "FileExistsError",
            "details": f"File '{db_filepath}' already exists."
          }
        }
    
    db_id = generate_id()
    title = title or db_filepath.split("/")[-1].split(".")[0]
    created_at = current_datetime_iso()
    description = description or ""
    initial_collections = initial_collections or []
    db_info = {
        "id": db_id,
        "title": title, 
        "description": description,       
        "created_at": created_at,
        "updated_at": created_at,        
    }
    if owner:
        db_info["owner"] = owner
    if tags:
        db_info["tags"] = tags

    collections = {name: [] for name in initial_collections}

    db = {
        "db_info": db_info,
        "collections": collections
    }

    json_db_save(db_filepath, db)
    return {
      "success": True,
      "message": "Database file created successfully.",
      "data": {
        "db_id": db_id,
        "db_path": db_filepath
      }
    }


@tool(category='database')
def json_db_get_entry(db_filepath: str, collection: str, entry_id: str) -> dict:
    """
    Retrieve a single entry by ID from the database.
    Args:
        filepath (str): Database file path
        collection (str): Collection name
        entry_id (str): Entry ID to find
    Returns:
        dict: Entry data or None if not found
    """
    db = json_db_load(db_filepath)
    # return next((entry for entry in db.get(collection, []) if entry["id"] == entry_id), None)
    for entry in db.get("collections", {}).get(collection, []):
        if entry["id"] == entry_id:
            return entry
    return None


@tool(category='database')
def json_db_get_collection(db_filepath: str, collection: str) -> dict:
    """
    Retrieve all entries from a specified collection in the database.
    
    Args:
        db_filepath (str): Path to the database file
        collection (str): Name of the collection to retrieve
        
    Returns:
        dict: Response object with success status and data
        Example:
            {
                "success": True,
                "message": "Collection retrieved successfully.",
                "data": {
                    "collection_name": "entries",
                    "total_entries": 5,
                    "entries": [...]
                }
            }
            {"success": False, "message": "Database file not found."}
            {"success": False, "message": "Collection not found."}
    """
    db = json_db_load(db_filepath)
    if not db:
        return {"success": False, "message": "Database file not found."}
    
    collection_data = db.get("collections", {}).get(collection)
    if collection_data is None:
        return {"success": False, "message": "Collection not found."}
        
    return {"success": True, "message": "Collection retrieved successfully.", "data": {"collection_name": collection, "total_entries": len(collection_data), "entries": collection_data}}


@tool(category='database')
def json_db_add_entry(db_filepath: str, collection: str, entry: dict, add_createdat: bool = None, add_updatedat: bool = None) -> str:
    """
    Add a new entry to a collection in the JSON database.

    Args:
        db_filepath (str): Path to the database file
        collection (str): Collection name 
        entry (dict): Entry data to add
        add_createdat (bool): If True, adds created_at timestamp to entry (optional)
        add_updatedat (bool): If True, adds updated_at timestamp to entry (optional)

    Returns:
        dict: Response object with success status and message
        Example:
        {
            "success": True,
            "message": "Entry added successfully.",
            "data": {"entry_id": "abc123"}
        }
    Raises:
        Exception: With specific message if validation fails.
    """
    db_data = json_db_load(db_filepath)
    if not db_data:
        raise Exception("Database file not found.")
    if not collection:
        raise Exception("Collection name (str) is required.")
    if not entry:
        raise Exception("Entry (dict) is required.")

    if "collections" not in db_data:
        db_data["collections"] = {}
    if collection not in db_data["collections"]:
        db_data["collections"][collection] = []

    entry_datetime = current_datetime_iso()

    # Check schema for required timestamps
    if "db_json_schema" in db_data:
        schema = db_data["db_json_schema"]
        if "collections" in schema.get("properties", {}):
            collection_schema = schema["properties"]["collections"]["properties"].get(collection, {})
            if "items" in collection_schema:
                required_fields = collection_schema["items"].get("required", [])
                if "created_at" in required_fields and "created_at" not in entry:
                    entry["created_at"] = entry_datetime
                if "updated_at" in required_fields and "updated_at" not in entry:
                    entry["updated_at"] = entry_datetime

    entry_id = entry.get("id", generate_id())
    entry["id"] = entry_id
    if add_createdat and "created_at" not in entry:
        entry["created_at"] = entry_datetime
    if add_updatedat and "updated_at" not in entry:
        entry["updated_at"] = entry_datetime

    db_data["collections"][collection].insert(0, entry)

    if "db_info" in db_data:
        db_data["db_info"]["updated_at"] = entry_datetime

    json_db_save(db_filepath, db_data)

    return {
        ResponseKey.STATUS: ResponseStatus.SUCCESS,
        ResponseKey.DATA: {"entry_id": entry_id},
        ResponseKey.MESSAGE: {
            ResponseKey.TITLE: "Entry added to JSON DB",
            ResponseKey.BODY: f"db file path: {db_filepath}, \ncollection: {collection}, \nentry id: {entry_id}"
        }
    }


@tool(category='database')
def json_db_update_entry(db_filepath: str, collection: str, entry_id: str, updates: dict) -> bool:
    """
    Update an existing entry by ID in the JSON database.
    Args:
      db_filepath (str): Path to the database file
      collection (str): Collection name
      entry_id (str): ID of the entry to update
      updates (dict): Dictionary containing the fields and values to update
    Returns:
      dict: Response object with success status and message
      Example:
        {"success": True, "message": "Entry updated successfully.", "data": {"entry_id": "abc123"}}
        {"success": False, "message": "Database file not found."}
        {"success": False, "message": "Entry not found."}
    """
    db = json_db_load(db_filepath)
    if not db:
       return {"success": False, "message": "Database file not found."}
    for entry in db.get("collections", {}).get(collection, []):
        if entry["id"] == entry_id:
            entry_datetime = current_datetime_iso()

            # Check schema for required timestamps
            if "db_json_schema" in db:
              schema = db["db_json_schema"]
              if "collections" in schema.get("properties", {}):
                collection_schema = schema["properties"]["collections"]["properties"].get(collection, {})
                if "items" in collection_schema:
                  required_fields = collection_schema["items"].get("required", [])                  
                  if "created_at" in required_fields and "created_at" not in entry:
                    updates["created_at"] = entry_datetime                    
                  if "updated_at" in required_fields and "updated_at" not in entry:
                    updates["updated_at"] = entry_datetime

            entry.update(updates)
            if "db_info" in db:
              db["db_info"]["updated_at"] = entry_datetime
            json_db_save(db_filepath, db)
            return {"success": True, "message": "Entry updated successfully.", "data": {"entry_id": entry_id}}
    return {"success": False, "message": "Entry not found."}


@tool(category='database')
def json_db_delete_entry(db_filepath: str, collection: str, entry_id: str) -> bool:
    """
    Delete an entry by ID from the database.
    Args:
      db_filepath (str): Path to the database file
      collection (str): Collection name 
      entry_id (str): ID of the entry to delete
    Returns:
      dict: Response object with success status and message
      Example:
        {"success": True, "message": "Entry deleted successfully.", "data": {"entry_id": "abc123"}}
        {"success": False, "message": "Database file not found."}
        {"success": False, "message": "Entry not found."}
    """
    db = json_db_load(db_filepath)
    db_collection = db.get("collections", {}).get(collection, [])
    original_len = len(db_collection)
    db["collections"][collection] = [e for e in db_collection if e["id"] != entry_id]
    if len(db["collections"][collection]) < original_len:
        if "db_info" in db:
            db["db_info"]["updated_at"] = current_datetime_iso()
        json_db_save(db_filepath, db)
        return {"success": True, "message": "Entry deleted successfully.", "data": {"entry_id": entry_id}}
    return {"success": False, "message": "Entry not found."}


def brave_search(query: str, count: int = 5) -> Dict[str, Any]:
    """
    Search the web using Brave Search API.    
    Args:
        query (str): The search query
        count (int): Number of results to return (max 20)    
    Returns:
        Dict containing search results
    """
    api_key = os.getenv('BRAVE_API_KEY')
    if not api_key:
        raise ValueError("BRAVE_API_KEY environment variable is not set")
    base_url = "https://api.search.brave.com/res/v1/web/search"    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }    
    params = {
        "q": query,
        "count": min(count, 20),  # Ensure we don't exceed API limit
        "text_decorations": False,
        "search_lang": "en"
    }    
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Extract and format relevant information
    results = []
    if "web" in data and "results" in data["web"]:
        for result in data["web"]["results"]:
            results.append({
                "title": result.get("title", ""),
                "description": result.get("description", ""),
                "url": result.get("url", "")
            })
    
    return {
        "success": True,
        "results": results
    }
        
    


@tool()
def download_web_sourcecode(url: str) -> str:
    """
    Download the content of a web page.
    Args:
        url (str): The URL of the web page to download
    Returns:
        str: The content of the web page
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text


@tool()
def download_web_readable_content(url: str, css_selector: str = None) -> str:
    """
    Download and extract content from a web page, optionally filtered by CSS selector.
    Args:
        url (str): The URL of the web page to download
        css_selector (str, optional): CSS selector to filter content (e.g. "body main", "article", ".content")
    Returns:
        str: The extracted text content of the web page
    """
    from bs4 import BeautifulSoup
    
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for element in soup.find_all(['script', 'style']):
        element.decompose()
        
    if css_selector:
        # Extract content from specified elements
        elements = soup.select(css_selector)
        if elements:
            # Join text from all matching elements
            return '\n\n'.join(element.get_text(separator=' ', strip=True) 
                        for element in elements)
        else:
            return f"No elements found matching selector: {css_selector}"
    else:
        # Return all text if no selector specified
        return soup.get_text(separator=' ', strip=True)
            


@tool()
def crawl_website_for_urls(start_url: str, url_pattern: str = None, max_pages: int = 100) -> list:
    """
    Crawls a website starting from a given URL and collects all unique URLs containing a specific pattern.
    
    Args:
        start_url (str): The URL to start crawling from
        url_pattern (str): Only collect URLs containing this pattern (optional)
        max_pages (int): Maximum number of pages to crawl (default 100)
    
    Returns:
        list: List of unique URLs found
    """
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    
    visited_urls = set()
    found_urls = set()
    urls_to_visit = {start_url}
    base_domain = urlparse(start_url).netloc

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue
            
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            visited_urls.add(current_url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                url = urljoin(current_url, link['href'])
                
                # Skip if not same domain or invalid URL
                if not url.startswith('http') or urlparse(url).netloc != base_domain:
                    continue
                    
                # If pattern is specified, only collect matching URLs
                if url_pattern:
                    if url_pattern in url:
                        found_urls.add(url)
                else:
                    found_urls.add(url)
                    
                if url not in visited_urls:
                    urls_to_visit.add(url)
                    
        except Exception as e:
            print(f"Error processing {current_url}: {str(e)}")
            continue
            
    return list(found_urls)


@tool()
def extract_urls_from_pages(urls: list, css_selector: str) -> list:
    """
    Extracts all unique URLs from specified elements within each page.
    
    Args:
        urls (list): List of URLs to process
        css_selector (str): CSS selector to locate elements containing links
        
    Returns:
        list: List of unique URLs found within the specified elements
    """
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    
    found_urls = set()
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find elements matching the CSS selector
            elements = soup.select(css_selector)
            
            for element in elements:
                # Find all links within the selected elements
                for link in element.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    if full_url.startswith('http'):  # Only add valid URLs
                        found_urls.add(full_url)
                        
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue
            
    return list(found_urls)

@tool()
def slugify(text: str) -> str:    
    """
    Convert text to URL-friendly slug.
    Handles Czech characters and special characters according to best practices.
    
    Args:
        text (str): Input text to be converted
        
    Returns:
        str: Slugified string
        
    Examples:
        >>> slugify("Příliš žluťoučký kůň")
        'prilis-zlutoucky-kun'
        >>> slugify("Hello @ World!")
        'hello-world'
        >>> slugify("Product (2023) -- Special Edition")
        'product-2023-special-edition'
    """
    import re
    from unidecode import unidecode
    text = text.lower()
    text = unidecode(text)
    text = re.sub(r'[&@#%()[\]{}<>*+\\|/=~`\'"]', '-', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text


@tool()
def encode_image_to_base64(file_path):
    """Convert an image file to base64 string representation."""
    
    import base64
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@tool()
def extract_text_from_image_mistral_ocr(file_path):
    """Extract text from an image using Mistral OCR API."""
    if not file_path:
        raise ValueError("File path is required")
    """
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("File is not an image")
    """
    API_KEY = os.getenv("MISTRAL_API_KEY")
    API_BASE_URL = "https://api.mistral.ai/v1/ocr"
    MODEL = "mistral-ocr-latest"
    ext = os.path.splitext(file_path)[1].lower()
    mime_type = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.bmp': 'image/bmp',
      '.webp': 'image/webp'
    }.get(ext, 'image/jpeg')
    base64_encoded = encode_image_to_base64(file_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "document": {
          "type": "image_url",
          "image_url": f"data:{mime_type};base64,{base64_encoded}"
        }
    }
    response = requests.post(API_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result.get("pages", [])[0].get("markdown", "")


@tool()
def extract_text_from_image_openai(file_path, model=None):
    """Extract text from an image using OpenAI ChatGPT API."""
    if not file_path:
        raise ValueError("File path is required")
    API_KEY = os.getenv("OPENAI_API_KEY")
    API_BASE_URL = "https://api.openai.com/v1/chat/completions"
    if not model:
        model = "gpt-4o-mini"
    file_extention = os.path.splitext(file_path)[1].lower()
    mime_type = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.bmp': 'image/bmp',
      '.webp': 'image/webp'
    }.get(file_extention, 'image/jpeg')
    base64_image = encode_image_to_base64(file_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract and transcribe all text from this image. Output in the original language. Output only the text in pure plain text format without any explanations or comments."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "temperature": 0,
        "max_tokens": 4096
    }
    response = requests.post(API_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]


@tool()
def commit_to_github(files: list, commit_message: str, repo_name: str, branch: str = "main") -> dict:
    """
    Commits and pushes files to a GitHub repository.
    
    Args:
        files (list): List of file paths to commit
        commit_message (str): Commit message
        repo_name (str): Name of repository in format "owner/repo"
        branch (str): Branch name to commit to (default: "main")
        
    Returns:
        dict: Result of the operation containing status and details
        
    Example:
        >>> files = ["posts/post1.md", "posts/post2.md"]
        >>> result = commit_to_github(
        ...     files=files,
        ...     commit_message="Add new blog posts",
        ...     repo_name="username/blog-repo"
        ... )
    """
    try:
        from github import Github
        import base64
        import os

        # Get GitHub token from environment
        github_token = os.getenv('GITHUB_ACCESS_TOKEN')
        if not github_token:
            return {
                "success": False,
                "error": "GITHUB_ACCESS_TOKEN environment variable not set"
            }

        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(repo_name)

        # Get the branch reference
        ref = f"heads/{branch}"
        branch_ref = repo.get_git_ref(ref)
        branch_sha = branch_ref.object.sha
        base_tree = repo.get_git_tree(branch_sha)

        # Create blob for each file
        element_list = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Create blob
                    blob = repo.create_git_blob(content, "utf-8")
                    element = {
                        "path": file_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    }
                    element_list.append(element)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error processing file {file_path}: {str(e)}"
                }

        # Create tree
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(branch_sha)
        
        # Create commit
        commit = repo.create_git_commit(
            message=commit_message,
            tree=tree,
            parents=[parent]
        )
        
        # Update branch reference
        branch_ref.edit(commit.sha)

        return {
            "success": True,
            "details": {
                "commit_sha": commit.sha,
                "commit_url": commit.html_url,
                "files_committed": len(files)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


