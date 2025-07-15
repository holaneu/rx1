import inspect
from app.utils.response_types import ResponseKey, ResponseAction, ResponseStatus

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
        self.func_log = []
        self.task_id = task_id  # Store task_id for usage within the instance

    def set_task_id(self, task_id):
        """Set the task_id for this workflow instance."""
        self.task_id = task_id

    def add_to_func_log(self, msg=None, msgTitle=None, msgBody=None):
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
    
    def success_response(self, data, msgTitle=None, msgBody=None):
        """Format a successful workflow response."""
        from datetime import datetime
        return {
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
    
    def error_response(self, error, msgTitle=None, msgBody=None):
        """Format an error workflow response."""
        from datetime import datetime
        return {
            ResponseKey.STATUS: ResponseStatus.ERROR,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.ERROR: str(error),
            ResponseKey.TIMESTAMP: datetime.now().timestamp(),
            ResponseKey.FUNC_LOG: self.get_func_log(),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: msgTitle or "Workflow failed",
                ResponseKey.BODY: msgBody or str(error)
            },
            ResponseKey.TASK_ID: self.task_id 
        }

    def interaction_request(self, msgTitle=None, msgBody=None, message: dict=None):
        """Helper to format an interaction request response."""
        from datetime import datetime
        return {
            ResponseKey.STATUS: ResponseStatus.PENDING,
            ResponseKey.ACTION: ResponseAction.INTERACTION_REQUEST,
            ResponseKey.TIMESTAMP: datetime.now().timestamp(),
            ResponseKey.FUNC_LOG: self.get_and_clear_func_log(),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: msgTitle or "User Interaction Required",
                ResponseKey.BODY: msgBody
            },
            ResponseKey.TASK_ID: self.task_id 
        }

