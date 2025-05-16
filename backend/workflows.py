# workflows.py
# Assuming app.py is in the same directory or Python path.
# If app.py is the main script, you might need to structure imports carefully
# to avoid circular dependencies if workflow_manager is defined in app.py.
# A common pattern is to define WorkflowManager in a separate core.py,
# then import it in both app.py and workflows.py.
# For simplicity here, we assume workflow_manager is accessible.

from app import workflow_manager # This should now get the fully initialized manager
import time

@workflow_manager.register_workflow(display_name="Simple Text Echo", description="Echoes the input with some steps.")
def simple_echo_workflow(main_input=None, progress=None, interact=None, **kwargs):
    """
    A basic workflow that demonstrates progress updates using the main input.
    """
    progress("Workflow Started", "Initializing simple echo...")
    time.sleep(0.5)

    progress("Processing Input", f"Received input: '{main_input}'")
    time.sleep(1)

    processed_text = f"The server processed your text: '{main_input.upper() if main_input else 'NO INPUT'}'"
    progress("Processing Complete", processed_text)
    time.sleep(0.5)
    
    return {"status": "success", "message": "Simple Echo Workflow Completed", "echo": processed_text}

@workflow_manager.register_workflow(display_name="Interactive Confirmation", description="Asks for confirmation after processing input.")
def interactive_confirm_workflow(main_input=None, progress=None, interact=None, **kwargs):
    """
    A workflow that takes main input, processes it, then asks for user confirmation.
    """
    progress("Interactive Workflow Started", f"Received input: '{main_input}'")
    time.sleep(1)

    initial_data = main_input or "default data"
    progress("Initial Processing", f"Working with: {initial_data}")
    
    # User interaction
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
        return {"status": "success", "message": final_result, "user_comments": user_decision.get('comments')}
    else:
        progress("Action Cancelled", "User chose not to proceed or no decision was made.")
        return {"status": "cancelled", "message": "Workflow cancelled by user."}

# Add more workflow functions here, decorated with @workflow_manager.register_workflow()