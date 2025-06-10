import inspect

WORKFLOWS_REGISTRY2 = {}

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
        WORKFLOWS_REGISTRY2[func.id] = {
            'name': func.name,
            'description': func.description,
            'function': func,
            'model': func.model,
            'category': func.category,
            'type': "workflow",
            'input_required': func.input_required,
            'module': func.__module__,
        }
        return func
    return decorator
