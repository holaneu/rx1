from workflows.registry import workflow
from utils.response_types import *

def collect_message(collection, title, body):
    collection.append({
        ResponseKey.TITLE: title,
        ResponseKey.BODY: body
    })

@workflow(category="Test")
def test_raise(task_id):
    """testing workflow"""
    try:          
        collected_messages = []

        data = list(range(6))

        collect_message(collected_messages, "Simulated date generated v2", data)

        if len(data) <= 6:
            raise RaisedError("data length is too short")

        collect_message(collected_messages, "Condition matched", f"Data length is {len(data)}, which is sufficient for processing.")     

        return response_output_success({
            ResponseKey.DATA: data,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE:"test_raise completed successfully",
                ResponseKey.BODY: f"Processed {len(data)} items"
            },
            ResponseKey.TASK_ID: task_id,
            ResponseKey.COLLECTED_MESSAGES: collected_messages
        })   
    
    except Exception as e:
        return response_output_error({
            ResponseKey.ERROR: str(e),
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.TASK_ID: task_id,
            ResponseKey.COLLECTED_MESSAGES: collected_messages
        })
