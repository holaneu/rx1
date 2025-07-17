import inspect

ASSISTANTS_REGISTRY = {}

def assistant(**kwargs):
    def decorator(func):
        func.name = func.__name__
        func.title = kwargs.get('name', func.__name__.replace('assistant_', '').replace('_', ' '))
        func.description = kwargs.get('description', func.__doc__)
        func.model = kwargs.get('model', None)
        func.category = kwargs.get('category', None)
        func.__module__ = func.__module__

        # Detect if input is required (by name and default absence)
        func.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )

        # Register automatically
        ASSISTANTS_REGISTRY[func.name] = {
            'name': func.name,
            'title': func.title,
            'description': func.description,
            'function': func,
            'model': func.model,
            'category': func.category,
            'type': "assistant",
            'input_required': func.input_required,        
            'module': func.__module__
        }
        return func
    return decorator
