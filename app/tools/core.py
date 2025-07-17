import inspect

TOOLS_REGISTRY = {}

def tool(**kwargs):
    def decorator(func):
        func.name = func.__name__
        func.title = kwargs.get('name', func.__name__.replace('tool_', '').replace('_', ' '))
        func.description = kwargs.get('description', func.__doc__)
        func.category = kwargs.get('category', None)
        func.__module__ = func.__module__

        
        """
        # Detect if input is required (by name and default absence)
        func.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )
        """

        # Register automatically
        TOOLS_REGISTRY[func.name] = {
            'name': func.name,
            'title': func.title,
            'description': func.description,
            'function': func,
            'category': func.category,
            'type': "tool",
            'module': func.__module__
        }
        return func
    return decorator
