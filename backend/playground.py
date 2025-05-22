from workflows import WORKFLOWS_REGISTRY
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
  
# ------
testing_registries()