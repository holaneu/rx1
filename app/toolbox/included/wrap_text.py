from app.toolbox.core import toolbox

@toolbox(name="Wrap Text", description="Wraps the input text with a specific format")
def test_wrap_text(input):
    try:
        wrapped_text = "... " + input.strip() + " ..."
        return wrapped_text
    except Exception as e:
        raise Exception(f"Error wrapping text: {e}")