from workflows.registry import workflow
from utils.shared import put_status_to_queue
from utils.response_types import *

@workflow(category="Test")
def test_more_wfs_1(task_id):
    """testing workflow"""
    try:
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Start working ...",
            ResponseKey.BODY: "Initializing workflow…"
        })    
        data = list(range(5))
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Operation done",
            ResponseKey.BODY: f"Received {len(data)} items"
        })
        return response_output_success({
            ResponseKey.DATA: data,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE:"test_more_wfs_1 completed successfully",
                ResponseKey.BODY: f"Processed {len(data)} items"
            },
            ResponseKey.TASK_ID: task_id
        })
    except Exception as e:
        return response_output_error({
            ResponseKey.ERROR: str(e),
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Workflow failed",
                ResponseKey.BODY: str(e)
            },
            ResponseKey.TASK_ID: task_id
        })
    

@workflow(category="Test")
def test_more_wfs_2(task_id):
    """testing workflow"""
    try:
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Start working ...",
            ResponseKey.BODY: "Initializing workflow…"
        })    
        data = list(range(5))
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Operation done",
            ResponseKey.BODY: f"Received {len(data)} items"
        })
        return response_output_success({
            ResponseKey.DATA: data,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE:"test_more_wfs_2 completed successfully",
                ResponseKey.BODY: f"Processed {len(data)} items"
            },
            ResponseKey.TASK_ID: task_id
        })
    except Exception as e:
        return response_output_error({
            ResponseKey.ERROR: str(e),
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FAILED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Workflow failed",
                ResponseKey.BODY: str(e)
            },
            ResponseKey.TASK_ID: task_id
        })
