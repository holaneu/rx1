import inspect
from datetime import datetime
import json
import os
from app.utils.response_types import ResponseKey, ResponseAction, ResponseStatus
from app.tools.included import save_to_file, user_data_files_path

# Define a registry to hold all workflows
# This allows for dynamic discovery and management of workflows
WORKFLOWS_REGISTRY = {}

# Decorator to register a function as a workflow
# This decorator can be used to annotate functions that should be treated as workflows
def workflow(**kwargs):
    def decorator(func):
        func.name = func.__name__
        func.title = kwargs.get('name', func.__name__.replace('workflow_', '').replace('_', ' '))
        func.description = kwargs.get('description', func.__doc__)
        func.model = kwargs.get('model', None)
        func.category = kwargs.get('category', None)
        func.is_workflow = True
        func.__module__ = func.__module__

        # Detect if input is required (by name and default absence)
        func.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )

        # Register automatically
        WORKFLOWS_REGISTRY[func.name] = {
            'name': func.name,
            'title': func.title,
            'description': func.description,
            'function': func,
            'model': func.model,
            'category': func.category,
            'type': "workflow",
            'input_required': func.input_required,
            'module': func.__module__,
        }
        return func
    return decorator


# Workflow class to manage workflow execution and logging
class Workflow:
    

    def __init__(self, task_id=None):
        import sys
        self.func_log = []
        self.wf_log = []
        self.task_id = task_id  # Store task_id for usage within the instance
        frame = sys._getframe(1)
        self.called_from = frame.f_code.co_name

    def set_task_id(self, task_id):
        """Set the task_id for this workflow instance."""
        self.task_id = task_id

    def add_msg_to_log(self, msg=None, msgTitle=None, msgBody=None):
        """Add a dict message to the func_log list."""
        msg = msg or {}
        title = msg.get("title") or msgTitle
        body = msg.get("body") if msg.get("body") is not None else msgBody
        body = body if body is not None else ""
        message = {
            ResponseKey.TITLE: title,
            ResponseKey.BODY: body
        }
        self.func_log.append(message)
        self.wf_log.append(message)

    def get_wf_log(self):
        """Return the current state of wf_log."""
        return self.wf_log.copy()
    
    def get_func_log(self):
        """Return the current state of func_log."""
        return self.func_log.copy()

    def get_and_clear_func_log(self):
        """Return the latest state and clear func_log."""
        messages = self.func_log.copy()
        self.func_log.clear()
        return messages
    
    def get_assistant_output_or_raise(self, assistant_output):
        """Extracts the message content from an assistant output or raises an error if not found."""
        if not assistant_output or 'message' not in assistant_output:
            raise Exception("Assistant output is empty or does not contain a message.")        
        message = assistant_output['message']
        if 'content' not in message:
            raise Exception("Message does not contain content.")        
        return message['content'].strip()
    
    def _save_log_file(self):
        try:
            timestamp = datetime.now()
            formatted_time = timestamp.strftime('%Y%m%d_%H%M%S')
            task_id_part = self.task_id or 'unknown'
            log_filepath = user_data_files_path(f"logs/workflow_{formatted_time}_{task_id_part}.log")

            log_data = {
                "name": self.called_from,
                "task_id": task_id_part,
                "timestamp": timestamp.isoformat(),
                "log": self.get_wf_log()
            }

            log_content = json.dumps(log_data, ensure_ascii=False, indent=2)
            save_to_file(content=log_content, filepath=log_filepath)

        except Exception as e:
            print(f"*** Error{e}") # Optional: print or log this error elsewhere if needed
            #pass  # Silently ignore to keep execution flow intact


    def success_response(self, data, msgTitle=None, msgBody=None):
        response = {
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.DATA: data,
            ResponseKey.TIMESTAMP: datetime.now().timestamp(),
            ResponseKey.FUNC_LOG: self.get_func_log(),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: msgTitle or "Workflow completed successfully",
                ResponseKey.BODY: msgBody or ""
            },
            ResponseKey.TASK_ID: self.task_id
        }
        self.wf_log.append(response.get(ResponseKey.MESSAGE))
        self._save_log_file()
        return response

    def error_response(self, error, msgTitle=None, msgBody=None):
        response = {
            ResponseKey.STATUS: ResponseStatus.ERROR,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.ERROR: str(error),
            ResponseKey.TIMESTAMP: datetime.now().timestamp(),
            ResponseKey.FUNC_LOG: self.get_func_log(),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: msgTitle or "Workflow not completed",
                ResponseKey.BODY: msgBody or str(error)
            },
            ResponseKey.TASK_ID: self.task_id
        }
        self.wf_log.append(response.get(ResponseKey.MESSAGE))
        self._save_log_file()
        return response

    def interaction_request(self, msgTitle=None, msgBody=None, message: dict=None, form_elements: list=None):
        from datetime import datetime
        response = {
            ResponseKey.STATUS: ResponseStatus.PENDING,
            ResponseKey.ACTION: ResponseAction.INTERACTION_REQUEST,
            ResponseKey.TIMESTAMP: datetime.now().timestamp(),
            ResponseKey.FUNC_LOG: self.get_and_clear_func_log(),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: msgTitle or "User Interaction Required",
                ResponseKey.BODY: msgBody,
                ResponseKey.FORM_ELEMENTS: form_elements or []
            },
            ResponseKey.TASK_ID: self.task_id
        }
        self.wf_log.append(response.get(ResponseKey.MESSAGE))

        return response
    