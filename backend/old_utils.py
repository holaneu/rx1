# DECORATORS

# Tool decorator
def tool(**kwargs):
  """Decorator to define tool functions with metadata."""
  def decorator(func):
      func.id = func.__name__  # Automatically set id to the function name
      func.name = kwargs.get('name', func.__name__.replace('', '').replace('_', ' '))  # Use function name as default name
      func.description = kwargs.get('description', func.__doc__)  # Use function docstring if no description
      func.category = kwargs.get('category', None)  # Assign None if category is not provided
      func.is_tool = True
      return func
  return decorator


# Assistant decorator
def assistant(**kwargs):
    """Decorator to define assistant functions with metadata."""
    def decorator(func):
        func.id = func.__name__  # Automatically set id to the function name
        func.name = kwargs.get('name', func.__name__.replace('assistant_', '').replace('_', ' '))  # Use function name as default name
        func.description = kwargs.get('description', func.__doc__)  # Use function docstring if no description
        func.model = kwargs.get('model', None)  # Assign None if model is not provided
        func.category = kwargs.get('category', None)  # Assign None if category is not provided
        func.is_assistant = True
        return func
    return decorator
