# SSE (Server-Sent Events) queue management for task status updates.
# This module provides functionality to manage Server-Sent Events (SSE) queues for tasks.

import queue
import time
from utils.response_types import ResponseKey

all_task_sse_queues: dict[str, queue.Queue] = {}

def put_msg_to_task_sse_queue(task_id: str, msgTitle: str = None, msgBody: str = None, message: dict = None):
    """Helper to enqueue a status message for SSE streaming."""
    task_sse_queue = all_task_sse_queues.get(task_id)
    if task_sse_queue:
        task_sse_item = {
            ResponseKey.TASK_ID: task_id,
            ResponseKey.TIMESTAMP:  time.time(),
            ResponseKey.MESSAGE: message or {
                ResponseKey.TITLE: msgTitle,
                ResponseKey.BODY: msgBody
            }
        }
        task_sse_queue.put(task_sse_item)

# Example usage:
#from utils.shared import put_msg_to_task_sse_queue
#put_msg_to_task_sse_queue(task_id=task_id, msgTitle="start ...", msgBody="Initializing workflow…") 