
from app import workflow_manager  # Import the existing instance instead of creating new one

wfs1 = list(workflow_manager.registered_funcs.keys())
wfs2 = workflow_manager.get_available_workflows_for_api()
print(wfs1)
print(wfs2)