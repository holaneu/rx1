# RX1 

RX1 is a lightweight, fully independent workflow automation app designed to run locally or on your own hosting—no reliance on Big Tech or hyperscalers. Everything you need is built in or easily extensible by adding your own code (functions, prompts), including its own private file storage system, so your ideas, tasks, and data remain completely under your control. While RX1 can connect to third-party tools, databases, AI providers, etc., it also works 100% offline for maximum privacy. At its core, RX1 embraces simplicity by returning to the roots: plain text files. Store your knowledge, code, questions, and even entire personal databases (using the JSON-based PerDB) in plain text. With extensible workflows, built-in tools, and optional AI assistants, RX1 brings together automation, creativity, and independence—all in one place.


## 🚀 Looking for Contributors!

I’m seeking collaborators to help bring the RX1 open-source project to a production-ready release! If you’re passionate about workflow automation, AI integration, or building extensible Python applications, I’d love to hear from you.

Whether you’re interested in coding, testing, documentation, UI/UX, sharing ideas, or managing GitHub projects, your help is welcome. Please review the Goals section and let us know if you’d like to join or contribute!


## Overview
The main concept of the app and its logic includes:  
- **Tools**, **AI assistants**, and **memory** combined together within **workflows** to automate tasks simply. Usage of AI is not necessary, AI is just one type of available actions (workflow steps) which user can utilize.  

- **Workflows** are the core pillar of the application. They define how sequences of actions are organized to complete a task automatically. A workflow consists of simply linear (sequential) steps, where Task A leads to Task B in a defined order. Workflows generally proceed from start to finish, but they can also include points where the user is prompted to make decisions — for example, to confirm and continue, stop the workflow, or retry a specific step.

  The result of a workflow is a completed task that may involve various automated operations. Workflows can utilize a combination of tools, assistants, and memory.  
  - **Example of a workflow:** Given an input phrase—ask AI to explain it in simple language with examples, save this explanation to a file, translate the description into another language, save the translation to another file, craft a short blog post about it, and publish the post live.

- **Tools** are functions capable of performing various operations—such as fetching responses from AI, opening files, saving files, transforming text, listing files in a directory, making API calls, and much more. The system is highly extensible: any function can be added as long as it can be written in the project’s programming language (currently Python). Once added, the function can be enabled for use. Additionally, one tool can call other tools (or functions) if needed.  

- **Assistants** are specialized functions designed to interact with AI using predefined text prompts to generate responses tailored to specific tasks. The assistant system is **extensible**, meaning new assistant functions can be easily added to handle different types of AI interactions as needed.

- **Memory** refers to persistent data storage, allowing the system to retain and retrieve data as needed to support workflows and tasks. Currently, the system supports **storing data in local files**. However, the memory system is **extensible**, allowing for the addition of more storage types in the future, such as **database integrations**, **committing data to remote GitHub repositories** or other forms of persistent storage.


## **Goals**

The goal is to **gradually expand the app’s capabilities** while maintaining simplicity:
- **Simple UI workflow builder** — Sequential, without any drag-and-drop canvases. Users can build workflows by adding steps (functions, tools, assistants) one after another. Each workflow is stored as JSON in private user data, with options to run, edit, or remove it.
- **Cloud-hosted option** — The app should later support cloud deployment (simply using `git clone`, updating by `git pull`, etc.). The cloud option will make it accessible on mobile devices, with personal centralized storage for user assets, along with secure user authentication (sign-up and sign-in capabilities).
- **Plugin system** — Allow tools, functions, assistants, workflows, and prompts to be extended as modules or plugins, with two parallel resource pools: a "public/default" library distributed with the app, and a "private/personal" library stored in user data.
- **Prompts library** — Maintain a structured library of prompts to support reusable and consistent AI interactions.
- **Asynchronous functions** — Enable support for asynchronous execution of functions to improve performance and responsiveness. *(Nice to have)*
- **Realtime SSE messages** — Fix already implemented Server-Sent Events (SSE) for real-time updates and notifications in the UI. Now it doesn't work "real time" as expected, probably because of lack of async function?? *(Nice to have)*
- **Simplicity and independancy** — Focus on linear step processing. Keep the codebase as simple as possible. Prefer using Python’s built-in standard libraries over external packages whenever feasible, minimizing dependencies and making the system easier to maintain and extend.
- **Use classes** - Thinking about replace decorated functions by classes / instances, for workflows, tools, assistants etc.


## Details

### Technical Architecture

1. **Core Components**
   - **Decorator System**: Uses Python decorators (@workflow, @assistant, @tools) to define and categorize functionality
   - **Dynamic Registration**: Automatically discovers and registers workflows, tools, and assistants through introspection
   - **Modular Design**: Separates concerns into distinct component types:
     - Workflows (high-level task orchestration)
     - Tools (utility functions and operations)
     - Assistants (AI interaction handlers)

2. **AI Integration**
   - Supports multiple AI providers (OpenAI, Anthropic, Mistral and more)
   - Flexible model configuration system
   - Standardized response handling
   - Built-in error management and logging
   - Configurable API interactions

3. **Tool Framework**
   - File operations (read/write with safety checks)
   - Data transformation utilities
   - API interaction handlers
   - Logging and monitoring capabilities
   - Input/output formatting

4. **Assistant Framework**
   - Template-based prompt engineering
   - Consistent response formatting
   - Model-agnostic design
   - Built-in verbose mode for debugging
   - Default model fallbacks


## Quick Start

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd rx1
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env_template` to `.env` and fill in required values.
   - You can change the user_id value there (instead of default `test_user`)

4. **Run the app:**
   ```sh
   python main.py
   ```


## Directory Structure

| Folder           | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `app/assistants` | AI assistant definitions and logic                                      |
| `app/tools`      | Utility and integration functions ("tools")                             |
| `app/workflows`  | Workflow orchestration logic                                            |
| `app/storage`    | Persistent storage and models                                           |
| `app/utils`      | Shared utility functions and helpers                                    |
| `app/configs`    | Application configuration files and settings                            |
| `app/web`        | Web interface: HTML templates, static files (CSS, JS, images)           |
| `user_data/`     | User-generated data and workflow configs                                |
| `materials/`     | Documentation and terminology                                           |


## Extending RX1

To add a new workflow, tool or assistant, simply create a Python function and decorate it:

The system will auto-discover and register it.

Workflow example:

```python
from app.workflows.core import *
from app.tools.public import save_to_file, user_files_folder_path
from app.assistants.public import assistant_translator_cs_en

@workflow()
def translation_cs_en_basic_custom(task_id, input, model=None):
    """Translates text between Czech and English v2."""
    try:
        wf = Workflow()

        wf.add_to_func_log(msgTitle="Workflow Started", msgBody=f"Task ID: {task_id}, Input: {input}, Model: {model}")

        translated_text = wf.get_assistant_output_or_raise(assistant_translator_cs_en(input=input, model=model))
        
        wf.add_to_func_log(msgTitle="Translation Completed", msgBody=f"Translated text: {translated_text}")
        
        file_path = user_files_folder_path("translations.txt")
        save_to_file(file_path, translated_text + "\n\n-----\n", prepend=True)
        
        wf.add_to_func_log(msgTitle="Translation Saved to File", msgBody=f"File path: {file_path}")
        
        return wf.success_response(
            data=translated_text,
            msgBody=f"Result saved to {file_path}"
        )

    except Exception as e:
        return wf.error_response(error=e)
```