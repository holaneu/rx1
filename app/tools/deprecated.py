
from app.tools import tool

@tool()
def call_api_of_type_openai_official(model_name, input):
  from openai import OpenAI
  from app.tools import save_to_file, user_data_files_path, format_str_as_llm_message_obj, formatted_datetime
  import json
    
  client = OpenAI()
  try:
    completion = client.chat.completions.create(
      model=model_name,
      messages=format_str_as_llm_message_obj(input)
    )
    log_timestamp = formatted_datetime("%Y%m%d_%H%M%S") # datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filepath = user_data_files_path(f"logs/ai_response_{log_timestamp}.log")
    # Convert completion object to dictionary for JSON serialization
    completion_dict = {
      "model": completion.model,
      "choices": [{
        "message": {
          "content": completion.choices[0].message.content,
          "role": completion.choices[0].message.role
        }
      }],
      "usage": {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens
      }
    }    
    log_content = {
      "input": format_str_as_llm_message_obj(input),
      "output": completion_dict
    }
    log_content = json.dumps(log_content, ensure_ascii=False, indent=2)
    save_to_file(content=log_content, filepath=log_filepath)
    output = {
        "status": "call_api_of_type_openai_official: Success",
        "message": {
          "content": completion.choices[0].message.content,
          "role": completion.choices[0].message.role,
        },        
        "info": {
          "model": completion.model,
          "prompt_tokens": completion.usage.prompt_tokens,
          "completion_tokens": completion.usage.completion_tokens,
          "total_tokens": completion.usage.total_tokens
        }
      }
    return output
  except Exception as e:
    print(f"Error calling OpenAI: {e}")
    return None
  

@tool()
def call_api_of_type_anthropic(model, messages):
  import requests
  import json
  from app.tools import get_llm_model_info, format_str_as_llm_message_obj

  model_data = get_llm_model_info(model['name'])
  if model_data is None:
    print("no model data")
    return None

  messages = format_str_as_llm_message_obj(messages)
  
  headers = {
    "x-api-key": model_data['api_key'],
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json"
  }

  payload = {
    "model": model_data['name'],
    "messages": messages,
    "max_tokens": 1024
  }

  try:
    response = requests.post(model_data['base_url'], headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
      result = response.json()
      return result["content"][0]["text"]
    else:
      print(f"Error: {response.status_code}")
      print(response.text)
      return None
  except Exception as e:
    print(f"Error calling model: {e}")
    return None