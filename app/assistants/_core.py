import inspect
import functools

from app.utils.registries import ASSISTANTS_REGISTRY

def assistant(**kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs_inner):
            try:
                return func(*args, **kwargs_inner)
            except Exception as e:
                raise Exception(f"[{func.__name__}]: {str(e)}.") from e

        # Metadata        
        wrapper.name = func.__name__
        wrapper.title = kwargs.get('name', func.__name__.replace('assistant_', '').replace('_', ' '))
        wrapper.description = kwargs.get('description', func.__doc__)
        wrapper.model = kwargs.get('model', None)
        wrapper.category = kwargs.get('category', None)
        wrapper.__module__ = func.__module__

        # Detect if input is required (by name and default absence)
        wrapper.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(wrapper).parameters.values()
        )

        # Register automatically
        ASSISTANTS_REGISTRY[wrapper.name] = {
            'name': wrapper.name,
            'title': wrapper.title,
            'description': wrapper.description,
            'function': wrapper,
            'model': wrapper.model,
            'category': wrapper.category,
            'type': "assistant",
            'input_required': wrapper.input_required,        
            'module': wrapper.__module__
        }
        return wrapper
    return decorator
