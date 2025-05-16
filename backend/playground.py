
from app import *
workflow_manager = WorkflowManager()
wfs = list(workflow_manager.registered_funcs.keys())
print(wfs)