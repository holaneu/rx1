import time
from shared import send_status_message  # import the SSE‐helper


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
        return func
    return decorator


@workflow(name="Test Workflow", category="Test")
def test1(task_id):
    """Workflow that demonstrates the use of status updates and user input. It fetches data from an API, waits for user confirmation, and then processes the data.
    """
    # Initialize the workflow
    send_status_message(task_id, {"title": "Started", "body": "Initializing workflow…"})
    
    # Do some work
    time.sleep(1)
    data = list(range(5))
    send_status_message(task_id, {
        "title": "API Fetched",
        "body": f"Received {len(data)} items"
    })

    # Now pause until the user confirms
    user_input = yield {
        "action": "interaction_request",
        "message": "Continue processing these items?"
    }

    # Resume once user_input is sent
    send_status_message(task_id, {
        "title": "Processing",
        "body": f"User said “{user_input}” — now processing…"
    })
    time.sleep(1)  # simulate more work

    send_status_message(task_id, {
        "title": "Almost done",
        "body": "Finalizing results…"
    })
    time.sleep(1)

    send_status_message(task_id, {
        "title": "Done",
        "body": "Workflow completed successfully."
    })

    return {
        "status": "success",
        "data":  f"Processed {len(data)} items."
    }


# ----------------------
# Registry of workflows - Extract all workflows dynamically
import inspect
WORKFLOWS_REGISTRY = {
    func.id: {
      'name': func.name, 
      'description': func.description, 
      'function': func, 
      'model': func.model, 
      'category': func.category
    }
    for name, func in inspect.getmembers(__import__(__name__), inspect.isfunction)
    if hasattr(func, 'id') and hasattr(func, 'is_workflow')  # Check for workflow marker
}