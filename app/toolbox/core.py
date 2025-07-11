import inspect

TOOLBOX_REGISTRY = {}

def toolbox(**kwargs):
    def decorator(func):
        func.id = func.__name__
        func.name = kwargs.get('name', func.__name__.replace('tool_', '').replace('_', ' '))
        func.description = kwargs.get('description', func.__doc__)
        func.category = kwargs.get('category', None)
        func.__module__ = func.__module__

        # Detect if input is required (by name and default absence)
        func.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )

        # Register automatically
        TOOLBOX_REGISTRY[func.id] = {
            'name': func.name,
            'description': func.description,
            'function': func,
            'category': func.category,
            'type': "tool",
            'module': func.__module__
        }
        return func
    return decorator
