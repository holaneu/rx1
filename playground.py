from app.workflows.core import WORKFLOWS_REGISTRY
import json

def testing_registries():

    print("WORKFLOWS_REGISTRY")
    print(WORKFLOWS_REGISTRY)

    print("WORKFLOWS_REGISTRY without functions")
    workflows_without_functions = {
        name: {k: v for k, v in workflow.items() if k != 'function'}
        for name, workflow in WORKFLOWS_REGISTRY.items()
    }
    print(json.dumps(workflows_without_functions, indent=2))
  
def testing_modular_workflows():
    """
    print("Testing modular workflows:")
    for name, workflow in WORKFLOWS_REGISTRY2.items():
        print(f"Workflow: {name}")
        print(f"  Description: {workflow['description']}")
        print(f"  Category: {workflow['category']}")
        print(f"  Input Required: {workflow['input_required']}")
        print(f"  Module: {workflow['module']}")
        print(f"  Function ID: {workflow['function'].id if 'function' in workflow else 'N/A'}")
        print()
    """
    print("WORKFLOWS_REGISTRY without functions")
    workflows_without_functions = {
        name: {k: v for k, v in workflow.items() if k != 'function'}
        for name, workflow in WORKFLOWS_REGISTRY.items()
    }
    print(json.dumps(workflows_without_functions, indent=2))

# ------
testing_modular_workflows()