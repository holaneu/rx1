from app.prompts import prompt, render_prompt_with_context


@prompt(name="Example prompt", description="Showcase task-oriented prompt rendering")
def prompt_example(*, name: str, task: str, projects: list=None, **extra):
    """Render a task-oriented prompt using Jinja2."""
    from datetime import date as dt
    # locals (locar variables) are automatically passed to the template
    var1 = dt.today().strftime("%Y-%m-%d")  # internal variable
    var2 = "some value"  # another internal variable
    _prompt = """
    Hello {{ name }}, today is {{ var1 }}
    Your task: {{ task }}
    {% if projects %}
    You have {{ projects | length }} projects:
    {% for p in projects %}
    - {{ p }}
    {% endfor %}
    {% endif %}
    """
    # Automatically merge locals and extra kwargs into context
    return render_prompt_with_context(_prompt.strip(), locals(), extra)


@prompt()
def output_without_comments():
    return "Output only the result and dont' write any comments or additional phrases.."


@prompt(name="Do Task", description="Render a task prompt")
def do_task(*, name: str, task: str, projects: list=None, **extra):
    """Render a task-oriented prompt using Jinja2."""
    from datetime import date as dt
    date = dt.today().strftime("%Y-%m-%d")  # internal variable
    _prompt = """
    Hello {{ name }}, today is {{ date }}
    Your task: {{ task }}
    {% if projects %}
    You have {{ projects | length }} projects:
    {% for p in projects %}
    - {{ p }}
    {% endfor %}
    {% endif %}
    """
    # Automatically merge locals and extra kwargs into context
    return render_prompt_with_context(_prompt.strip(), locals(), extra)


@prompt()
def correct_grammar(*, input: str, extra_instructions: str = None):
    """Corrects grammar where needed and returns corrected text"""
    output_format1 = output_without_comments()
    _prompt = """    
    Instructions: Correct grammar of the input text (Input).    
    {% if extra_instructions %}
    Extra instructions: {{extra_instructions}}.
    {% endif %}
    Output format: {{output_format1}}.
    Input: {{ input }}
    """
    return render_prompt_with_context(_prompt.strip(), locals())


@prompt()
def explain_swe_terms(*, input: str):
    """Explains a software engineering term in simple words."""
    output_format1 = output_without_comments()
    _prompt = """You are software engineer with expertise in software development and programming. You are given a text that contains a software engineering term. Your task is to explain this term in simple words.
    Output format: {{output_format1}}.
    Input: {{ input }}
    """
    return render_prompt_with_context(_prompt.strip(), locals())