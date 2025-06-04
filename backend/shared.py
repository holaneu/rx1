import queue
import time

status_queues: dict[str, queue.Queue] = {}

def put_status_to_queue(task_id: str, message: dict):
    """Helper to enqueue a status message for SSE streaming."""
    q = status_queues.get(task_id)
    if q:
        status_data = {
            "task_id": task_id,
            "timestamp":  time.time(),
            "message": message
        }
        q.put(message)
