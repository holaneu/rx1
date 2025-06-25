from workflows.core import *


@workflow( category="Test")
def test_multiple_yields_no_return(task_id):
    """testing workflow test3."""
    try:
        wf = Workflow(task_id=task_id)
        wf.add_to_func_log(msgTitle="Ahoj, zaciname", msgBody="Initializing workflow…")   
        data = list(range(5))
        wf.add_to_func_log(msgTitle="API Fetched", msgBody=f"Received {len(data)} items")
        user_input = yield wf.interaction_request(
            msgTitle="Confirmation Required 1",
            msgBody="Continue processing these items?"
        )
        wf.add_to_func_log(msgTitle="Processing", msgBody=f"User said “{user_input}” — now processing…")
        user_input2 = yield wf.interaction_request(
            msgTitle="Confirmation Required 2",
            msgBody="Continue processing these items?"
        )
        wf.add_to_func_log(msgTitle="Processing", msgBody=f"User said “{user_input2}” — now processing…")
        yield wf.success_response(
            data=data,
            msgBody=f"Processed {len(data)} items"
        )
        
    except Exception as e:
        yield wf.error_response(error=e)