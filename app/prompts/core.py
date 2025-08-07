import functools
import inspect
from jinja2 import Template
from typing import Any, Dict, Tuple, Callable

# Registry to keep track of all prompt functions
PROMPTS_REGISTRY: Dict[str, Dict[str, Any]] = {}

def render_prompt_with_context(template: str, _locals: dict, extra: dict = None) -> Tuple[str, Dict[str, Any]]:
    """
    Merge template, locals(), and extra kwargs into context for Jinja rendering.
    Removes private variables and 'prompt' key to avoid conflicts.
    """
    context = {k: v for k, v in _locals.items() if not k.startswith('_')}
    if extra:
        context.update(extra)
    return template, context

def prompt(**meta_kwargs):
    """
    Decorator for prompt functions:
    - Registers function metadata
    - Handles Jinja2 rendering automatically
    - Catches exceptions and raises with [func_name]: message
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs_inner):
            try:
                result = func(*args, **kwargs_inner)

                # Support two return formats:
                # 1. Just template string
                # 2. (template string, context dict)
                if isinstance(result, tuple):
                    prompt_str, context = result
                elif isinstance(result, str):
                    prompt_str, context = result, {}
                else:
                    raise ValueError("Prompt function must return either a string or (string, dict).")

                return Template(prompt_str).render(context)

            except Exception as e:
                raise Exception(f"[{func.__name__}]: {str(e)}.") from e

        # Attach metadata
        wrapper.name = func.__name__
        wrapper.title = meta_kwargs.get('name', func.__name__.replace('_', ' '))
        wrapper.description = meta_kwargs.get('description', func.__doc__)
        wrapper.model = meta_kwargs.get('model', None)
        wrapper.category = meta_kwargs.get('category', None)
        wrapper.__module__ = func.__module__

        # Detect if 'input' parameter is required
        wrapper.input_required = any(
            param.name == 'input' and param.default == param.empty
            for param in inspect.signature(func).parameters.values()
        )

        # Register function in global registry
        PROMPTS_REGISTRY[wrapper.name] = {
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
