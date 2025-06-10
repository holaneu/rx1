import time
from shared import put_status_to_queue  # import the SSE‐helper
from response_types import *


# ----------------------
# Workflow decorator
def workflow(**kwargs):
    """Decorator to define workflow functions with metadata."""
    def decorator(func):
        func.id = func.__name__  # Automatically set id to the function name
        func.name = kwargs.get('name', func.__name__.replace('workflow_', '').replace('_', ' '))  # Use function name as default name
        func.description = kwargs.get('description', func.__doc__)  # Use function docstring if no description
        func.model = kwargs.get('model', None)  # Assign None if model is not provided
        func.category = kwargs.get('category', None)  # Assign None if category is not provided
        func.is_workflow = True
        func.__module__ = __name__
        return func
    return decorator


# ----------------------
# Example workflow functions using the decorator

@workflow(name="Test Workflow 2", category="Test")
def test2(task_id):
    try:
        """testing workflow test2."""
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Ahoj, zaciname", 
            ResponseKey.BODY: "Initializing workflow…"
        })    
        data = list(range(5))
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "API Fetched", 
            ResponseKey.BODY: f"Received {len(data)} items"
        }) 
        user_input = yield response_output_interaction_request({
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Confirmation Required",
                ResponseKey.BODY: "Continue processing these items?"
            },
            ResponseKey.TASK_ID: task_id
        })
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Processing",
            ResponseKey.BODY: f"User said “{user_input}” — now processing…"
        })
        put_status_to_queue(task_id, {
            ResponseKey.TITLE: "Done",
            ResponseKey.BODY: "Workflow completed successfully."
        })
        user_input = yield response_output_interaction_request({
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Confirmation Required",
                ResponseKey.BODY: "Continue processing these items?"
            },
            ResponseKey.TASK_ID: task_id
        })
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Processing",
            ResponseKey.BODY: f"User said “{user_input}” — now processing…"
        })
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Done",
            ResponseKey.BODY: "Workflow completed successfully."
        })
        return response_output_success({
            ResponseKey.DATA: data,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE:"Workflow completed successfully",
                ResponseKey.BODY: f"Processed {len(data)} items"
            },
            ResponseKey.TASK_ID: task_id
        })
           
    except Exception as e:
        return response_output_error({
            ResponseKey.ERROR: str(e),
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Workflow failed",
                ResponseKey.BODY: str(e)
            },
            ResponseKey.TASK_ID: task_id
        })


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