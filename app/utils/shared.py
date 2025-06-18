import queue
import time

status_queues: dict[str, queue.Queue] = {}

def put_status_to_queue(task_id: str, message: dict):
    """Helper to enqueue a status message for SSE streaming."""
    task_status_queue = status_queues.get(task_id)
    if task_status_queue:
        task_status_item = {
            "task_id": task_id,
            "timestamp":  time.time(),
            "message": message
        }
        task_status_queue.put(task_status_item)

class RaisedError(Exception):
    """Custom exception for translation related errors"""
    pass