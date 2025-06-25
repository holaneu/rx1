from workflows.core import *

@workflow(category="Test")
def test_single_yield_single_return(task_id):
    """testing workflow test2."""
    try:
        wf = Workflow(task_id=task_id)
        wf.add_to_func_log(msgTitle="start ...", msgBody="Initializing workflow…")  
        data = list(range(5))
        wf.add_to_func_log(msgTitle="API Fetched", msgBody=f"Received {len(data)} items")
        user_input = yield wf.interaction_request(
            msgTitle="Confirmation Required",
            msgBody="Continue processing these items?"
        )
        wf.add_to_func_log(msgTitle="Processing", msgBody=f"User said “{user_input}” — now processing…")
        return wf.success_response(
            data=data,
            msgTitle="Workflow completed successfully",
            msgBody=f"Processed {len(data)} items"
        )
    except Exception as e:
        return wf.error_response(error=e)
