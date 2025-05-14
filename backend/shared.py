import queue

status_queues: dict[str, queue.Queue] = {}

def status(task_id: str, message: dict):
    """Helper to enqueue a status message for SSE streaming."""
    q = status_queues.get(task_id)
    if q:
        q.put(message)
