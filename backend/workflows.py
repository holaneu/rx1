import time
from shared import status  # import the SSE‐helper

def fetch_api():
    # Dummy stand-in for a real HTTP/API call
    time.sleep(1)
    return list(range(5))

def workflow(task_id):
    # Emit a status update immediately
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
