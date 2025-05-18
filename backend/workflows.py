import functools
from flask import session
import uuid
import logging
import time

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registry to store workflow definitions
workflows_registry = {}

def register_workflow(display_name=None, description=None):
    def decorator(func):
        workflow_name = func.__name__
        actual_display_name = display_name or workflow_name.replace('_', ' ').title()
        actual_description = description or func.__doc__ or "No description available."

        @functools.wraps(func)
        def wrapper(workflow_manager, main_input=None, *args, **kwargs):
            logger.info(f"Wrapper called for workflow: {workflow_name}")
            
            session_id = session.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['session_id'] = session_id

            workflow_instance_id = str(uuid.uuid4())
            workflow_manager.active_workflows[workflow_instance_id] = {
                'workflow_name': workflow_name,
                'session_id': session_id,
                'original_function': func,
                'main_input': main_input,
                'args': args,
                'kwargs': kwargs,
                'paused': False,
                'context': {}
            }
            
            workflow_manager.socketio_instance.start_background_task(
                workflow_manager._execute_workflow, workflow_instance_id)
            return workflow_instance_id

        workflows_registry[workflow_name] = {
            'id': workflow_name,
            'name': actual_display_name,
            'description': actual_description,
            'callable_wrapper': wrapper
        }
        
        logger.info(f"Workflow '{workflow_name}' registered as '{actual_display_name}'.")
        return wrapper
    return decorator

# Example workflow definitions
@register_workflow(
    display_name="Simple Text Echo",
    description="Echoes the input with some steps."
)
def simple_echo_workflow(main_input=None, progress=None, interact=None, **kwargs):
    """A basic workflow that demonstrates progress updates using the main input."""
    progress("Workflow Started", "Initializing simple echo...")
    time.sleep(0.5)

    progress("Processing Input", f"Received input: '{main_input}'")
    time.sleep(1)

    processed_text = f"The server processed your text: '{main_input.upper() if main_input else 'NO INPUT'}'"
    progress("Processing Complete", processed_text)
    time.sleep(0.5)
    
    return {"status": "success", "message": "Simple Echo Workflow Completed", "echo": processed_text}

@register_workflow(
    display_name="Interactive Confirmation",
    description="Asks for confirmation after processing input."
)
def interactive_confirm_workflow(main_input=None, progress=None, interact=None, **kwargs):
    """A workflow that takes main input, processes it, then asks for user confirmation."""
    progress("Interactive Workflow Started", f"Received input: '{main_input}'")
    time.sleep(1)

    initial_data = main_input or "default data"
    progress("Initial Processing", f"Working with: {initial_data}")
    
    user_decision = interact({
        "title": "Confirm Action",
        "description": f"You provided: '{initial_data}'. Do you want to proceed with further processing?",
        "fields": [
            {
                "type": "radio",
                "id": "confirmation",
                "label": "Your Choice:",
                "options": ["Yes, proceed", "No, cancel"],
                "default": "Yes, proceed",
                "required": True
            },
            {
                "type": "textarea",
                "id": "comments",
                "label": "Additional Comments (Optional):",
                "required": False
            }
        ]
    })

    if user_decision and user_decision.get('confirmation') == "Yes, proceed":
        progress("Confirmation Received", f"User confirmed. Comments: '{user_decision.get('comments', 'N/A')}'")
        time.sleep(1.5)
        final_result = f"Processing complete for '{initial_data}' with user confirmation."
        progress("Finalizing", final_result)
        return {
            "status": "success",
            "message": final_result,
            "user_comments": user_decision.get('comments')
        }
    else:
        progress("Action Cancelled", "User chose not to proceed or no decision was made.")
        return {"status": "cancelled", "message": "Workflow cancelled by user."}