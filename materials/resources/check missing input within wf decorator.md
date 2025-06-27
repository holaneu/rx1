import inspect
from functools import wraps
from app.utils.response_types import ResponseKey, ResponseStatus, ResponseAction

def workflow(**kwargs):
    def decorator(func):
        func.id = func.__name__
        func.name = kwargs.get('name', func.__name__.replace('workflow_', '').replace('_', ' '))
        func.description = kwargs.get('description', func.__doc__)
        func.model = kwargs.get('model', None)
        func.category = kwargs.get('category', None)
        func.is_workflow = True
        func.__module__ = func.__module__

        # Detect if input is required (by name and default absence)
        func.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )

        # Register automatically
        WORKFLOWS_REGISTRY[func.id] = {
            'name': func.name,
            'description': func.description,
            'function': func,
            'model': func.model,
            'category': func.category,
            'type': "workflow",
            'input_required': func.input_required,
            'module': func.__module__,
        }

        @wraps(func)
        def wrapper(*args, **fkwargs):
            # Universal input check
            sig = inspect.signature(func)
            bound = sig.bind(*args, **fkwargs)
            bound.apply_defaults()
            if 'input' in bound.arguments:
                value = bound.arguments['input']
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    # Option 1: raise Exception
                    # raise Exception("No input provided.")
                    # Option 2: return error response (recommended)
                    wf = Workflow()
                    return wf.error_response(
                        error="No input provided.",
                        msgTitle="Missing Input",
                        msgBody="You must provide input for this workflow."
                    )
            return func(*args, **fkwargs)
        return wrapper
    return decorator