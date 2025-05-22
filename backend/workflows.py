import time
from shared import send_status_message  # import the SSE‐helper
from workflow_types import WorkflowStatus, WorkflowAction, WorkflowMessage, WorkflowResult


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


@workflow(name="Test Workflow 1", category="Test")
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

    return WorkflowResult(
        status=WorkflowStatus.SUCCESS,
        action=WorkflowAction.WORKFLOW_FINISHED,
        message=WorkflowMessage(
            title="Workflow completed successfully",
            body=f"Processed {len(data)} items"
        ),
        data=data
    ).to_dict()

@workflow(name="Test Workflow 2", category="Test")
def test2(task_id, input):
    """Workflow that demonstrates the use of status updates and user input. It fetches data from an API, waits for user confirmation, and then processes the data.
    """
    send_status_message(task_id, {"title": "Started", "body": "Initializing workflow…"})    
    time.sleep(1)
    data = list(range(5))
    send_status_message(task_id, {
        "title": "API Fetched",
        "body": f"Received {len(data)} items"
    })
    time.sleep(0.1)
    user_input = yield {
        "action": "interaction_request",
        "message": "Continue processing these items?"
    }
    send_status_message(task_id, {
        "title": "Processing",
        "body": f"User said “{user_input}” — now processing…"
    })
    time.sleep(1)  # simulate more work
    send_status_message(task_id, {
        "title": "Done",
        "body": "Workflow completed successfully."
    })

    return WorkflowResult(
        status=WorkflowStatus.SUCCESS,
        action=WorkflowAction.WORKFLOW_FINISHED,
        message=WorkflowMessage(
            title="Workflow completed successfully",
            body=f"Processed {len(data)} items"
        ),
        data=data
    ).to_dict()


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