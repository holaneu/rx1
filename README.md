# RX1 

## Overview
The main concept of the app and its logic includes:  
- **Tools**, **AI assistants**, and **memory** combined together within **workflows** to automate tasks efficiently.  

- **Workflows** are the core pillar of the application. They define how sequences of actions are organized to complete a task automatically. A workflow can include different types of actions:
  - **Linear (sequential) steps:** where Task A leads to Task B in a specific order.
  - **Branching logic:** where tasks are triggered based on conditions or decision points.
  - **Parallel tasks:** where multiple actions run simultaneously to save time.  

  The result of a workflow is a completed task that may involve various automated operations. Workflows can utilize a combination of tools, assistants, and memory.  
  - **Example of a workflow:** Given an input phrase—ask AI to explain it in simple language with examples, save this explanation to a file, translate the description into another language, save the translation to another file, craft a short blog post about it, and publish the post live.

- **Tools** are functions capable of performing various operations—such as fetching responses from AI, opening files, saving files, transforming text, listing files in a directory, making API calls, and much more. The system is highly extensible: any function can be added as long as it can be written in the project’s programming language (currently Python). Once added, the function can be enabled for use. Additionally, one tool can call other tools (or functions) if needed.  

- **Assistants** are specialized functions designed to interact with AI using predefined text prompts to generate responses tailored to specific tasks. The assistant system is **extensible**, meaning new assistant functions can be easily added to handle different types of AI interactions as needed.

- **Memory** refers to persistent data storage, allowing the system to retain and retrieve data as needed to support workflows and tasks. Currently, the system supports **storing data in local files** and **committing data to remote GitHub repositories**. However, the memory system is **extensible**, allowing for the addition of more storage types in the future, such as **database integrations** or other forms of persistent storage.

### **Current and Long-Term Goals**

The current intention of the app's author is to use the application to automate various personal and work-related tasks. The goal is to **gradually expand the app’s capabilities** by continuously adding more tools, assistants, and workflows. The long-term vision is to make it easy and efficient to automate as many tasks as possible that can be automated.

At present, the application runs in a local environment and supports **API integrations over the internet** to extend its automation capabilities.  

The app includes a **set of predefined tools, assistants, and memory components**, but there’s an ongoing effort to **continuously add more features** to cover a wider range of automated tasks. This ensures the system remains flexible, adaptable, and capable of evolving alongside the user's automation needs.
  

## Details

## Application Overview
The application serves as a flexible workflow automation system that leverages AI capabilities through a modular architecture. It enables users to define, manage, and execute complex tasks involving AI interactions, text processing, and data management.

### User Perspective
From a user's standpoint, the application offers:

1. **Customizable Workflows**
   - Pre-defined workflows for common tasks like translation, text summarization, and situation analysis
   - Each workflow produces specific outputs that are automatically saved and organized
   - Results are stored in designated files for easy access and reference

2. **Key Features**
   - Translation services between Czech and English with YAML-formatted output
   - Text summarization capabilities for various content types
   - Situation analysis with structured breakdowns
   - Video transcript processing and chapter-based summarization
   - Simple lexicon generation with child-friendly explanations
   - Automatic logging and storage of all interactions

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


### UI and Server Components

1. **Simple Server Architecture**
  - Flask-based lightweight server (server.js)
  - Basic endpoints for core functionalities:
    - `/` - Serves the main interface
    - `/execute` - Handles workflow execution
    - `/list` - Returns available workflows
  - JSON responses for API calls
  - Basic error handling with status codes

2. **Minimalist Web Interface**
  - Single page application (index.html)
  - Simple workflow selection dropdown
  - Basic input text area
  - Execution button
  - Raw output display area

3. **Integration Layer**
  - Direct connection to workflow engine
  - Basic JSON data transformation
  - Simple error handling
  - Console-based logging