from workflows.core import *

@workflow(category="Test")
def test_single_return_no_yield(task_id):
    """testing workflow"""
    try:
        wf = Workflow(task_id=task_id)
        wf.add_to_func_log(msgTitle="start ...", msgBody="Initializing workflow…")
        data = list(range(5))        
        wf.add_to_func_log(msgTitle="Operation done", msgBody="Received {len(data)} items")
        return wf.success_response(
            data=data,
            msgTitle="Workflow completed successfully",
            msgBody=f"Processed {len(data)} items"
        )    
    except Exception as e:
        return wf.error_response(error=e)


@workflow(category="Test")
def test_single_yield(task_id):
    """testing workflow"""
    try:
        wf = Workflow(task_id=task_id)

        wf.add_to_func_log(msgTitle="start ...", msgBody="Initializing workflow…")

        data = list(range(5))
        
        wf.add_to_func_log(msgTitle="Operation done", msgBody="Received {len(data)} items")

        yield wf.success_response(
            data=data,
            msgTitle="Workflow completed successfully",
            msgBody=f"Processed {len(data)} items"
        )

    except Exception as e:
        return wf.error_response(error=e)