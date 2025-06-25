from workflows.core import *

@workflow(category="Test")
def test_raise(task_id):
    """testing workflow"""
    try:          
        wf = Workflow()

        data = list(range(7))

        #x = aaa # TEST: intentionally incorrect to test raising an exception

        wf.add_to_func_log(msgTitle="Simulated date generated v2", msgBody=data)     

        if len(data) <= 6:
            raise Exception("data length is too short")

        wf.add_to_func_log(msgTitle="Condition matched", msgBody=f"Data length is {len(data)}, which is sufficient for processing.")   

        return wf.success_response(
            data=data,
            msgTitle= "Test Raise Workflow",
            msgBody=f"Processed {len(data)} items successfully."
        )      
    
    except Exception as e:
        return wf.error_response(error=e)
        
