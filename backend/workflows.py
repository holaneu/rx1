import time
from shared import status  # import the SSE‐helper
from tools import fetch_api  # import the API call``
from utils import workflow  # import the workflow decorator

@workflow(name="Test Workflow", category="Test")
def test1(task_id):
    """Workflow that demonstrates the use of status updates and user input. It fetches data from an API, waits for user confirmation, and then processes the data.
    """
    # Initialize the workflow
    status(task_id, {"title": "Started", "body": "Initializing workflow…"})
    
    # Do some work
    data = fetch_api()
    status(task_id, {
        "title": "API Fetched",
        "body": f"Received {len(data)} items"
    })

    # Now pause until the user confirms
    user_input = yield {
        "action": "need_user_input",
        "message": "Continue processing these items?"
    }

    # Resume once user_input is sent
    status(task_id, {
        "title": "Processing",
        "body": f"User said “{user_input}” — now processing…"
    })
    time.sleep(1)  # simulate more work

    status(task_id, {
        "title": "Almost done",
        "body": "Finalizing results…"
    })
    time.sleep(1)

    status(task_id, {
        "title": "Done",
        "body": "Workflow completed successfully."
    })

    return "All done!"


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