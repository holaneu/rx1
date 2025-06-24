from workflows.core import *

@workflow(category="Test")
def test_raise(task_id):
    """testing workflow"""
    try:          
        wf = Workflow()

        data = list(range(7))

        wf.add_func_log("Simulated date generated v2", data)     

        if len(data) <= 6:
            raise Exception("data length is too short")

        wf.add_func_log("Condition matched", f"Data length is {len(data)}, which is sufficient for processing.")   

        return wf.workflow_success(
            data=data,
            msgTitle= "Test Raise Workflow",
            msgBody=f"Processed {len(data)} items successfully."
        )      
    
    except Exception as e:
        return wf.workflow_error(
            error=e
        )
        
