import inspect

TOOLS_REGISTRY = {}

import inspect
import functools

TOOLS_REGISTRY = {}  # Presumably already defined somewhere

def tool(**kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs_inner):
            try:
                return func(*args, **kwargs_inner)
            except Exception as e:
                raise Exception(f"[{func.__name__}] Error: {e}") from e

        # Metadata
        wrapper.name = func.__name__
        wrapper.title = kwargs.get('name', func.__name__.replace('tool_', '').replace('_', ' '))
        wrapper.description = kwargs.get('description', func.__doc__)
        wrapper.category = kwargs.get('category', None)
        wrapper.__module__ = func.__module__

        # Register automatically
        TOOLS_REGISTRY[wrapper.name] = {
            'name': wrapper.name,
            'title': wrapper.title,
            'description': wrapper.description,
            'function': wrapper,
            'category': wrapper.category,
            'type': "tool",
            'module': wrapper.__module__
        }

        return wrapper
    return decorator

