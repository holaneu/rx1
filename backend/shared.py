import queue

status_queues: dict[str, queue.Queue] = {}

def send_status_message(task_id: str, message: dict):
    """Helper to enqueue a status message for SSE streaming."""
    q = status_queues.get(task_id)
    if q:
        q.put(message)
