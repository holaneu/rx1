

def test_wrap_text(input):
    try:
        wrapped_text = "~~~ " + input.trim() + " ~~~"
        return wrapped_text
    except Exception as e:
        raise Exception(f"Error wrapping text: {e}")