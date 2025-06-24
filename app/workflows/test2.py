from workflows.core import workflow
from utils.shared import put_status_to_queue
from utils.response_types import *

@workflow(category="Test")
def test_single_yield_single_return(task_id):
    """testing workflow test2."""
    try:
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Ahoj, zaciname",
            ResponseKey.BODY: "Initializing workflow…"
        })    
        data = list(range(5))
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "API Fetched",
            ResponseKey.BODY: f"Received {len(data)} items"
        })
        user_input = yield response_output_interaction_request({
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: "Confirmation Required",
                ResponseKey.BODY: "Continue processing these items?"
            },
            ResponseKey.TASK_ID: task_id
        })
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Processing",
            ResponseKey.BODY: f"User said “{user_input}” — now processing…"
        })
        put_status_to_queue(task_id=task_id, message={
            ResponseKey.TITLE: "Done",
            ResponseKey.BODY: "Workflow completed successfully."
        })
        return response_output_success({
            ResponseKey.DATA: data,
            ResponseKey.ACTION: ResponseAction.WORKFLOW_FINISHED,
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE:"Workflow completed successfully",
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
