# DECORATORS
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


# Tool decorator
def tool(**kwargs):
  """Decorator to define tool functions with metadata."""
  def decorator(func):
      func.id = func.__name__  # Automatically set id to the function name
      func.name = kwargs.get('name', func.__name__.replace('', '').replace('_', ' '))  # Use function name as default name
      func.description = kwargs.get('description', func.__doc__)  # Use function docstring if no description
      func.category = kwargs.get('category', None)  # Assign None if category is not provided
      func.is_tool = True
      return func
  return decorator


# Assistant decorator
def assistant(**kwargs):
    """Decorator to define assistant functions with metadata."""
    def decorator(func):
        func.id = func.__name__  # Automatically set id to the function name
        func.name = kwargs.get('name', func.__name__.replace('assistant_', '').replace('_', ' '))  # Use function name as default name
        func.description = kwargs.get('description', func.__doc__)  # Use function docstring if no description
        func.model = kwargs.get('model', None)  # Assign None if model is not provided
        func.category = kwargs.get('category', None)  # Assign None if category is not provided
        func.is_assistant = True
        return func
    return decorator

# REMOVE:
# --- SSE helpers ---
# This module provides a simple way to send Server-Sent Events (SSE) from a Flask server.
import json
import queue
from flask import Response

# These will be initialized by app.py when the app starts
_status_queues: dict[str, queue.Queue] = {}

def init_status_queues(queues: dict):
    """Inject the shared status_queues dict from app.py."""
    global _status_queues
    _status_queues = queues

def status(task_id: str, message: dict):
    """Enqueue a status message for SSE streaming."""
    q = _status_queues.get(task_id)
    if q:
        q.put(message)

def make_sse_response(task_id: str) -> Response:
    """Return a Flask Response streaming SSEs for the given task_id."""
    q = _status_queues.get(task_id)
    if not q:
        # No such queue → 404
        return Response("", status=404)

    def event_stream():
        while True:
            msg = q.get()       # blocks until next status or None
            if msg is None:
                break
            payload = {"action": "status", "message": msg}
            yield f"data: {json.dumps(payload)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")