# app.py
from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit # Keep emit for direct use in socket handlers
import uuid
import functools
import json
import time
import logging # Import logging

# Configure basic logging for Flask app if not already configured elsewhere
logging.basicConfig(level=logging.INFO)


class WorkflowManager:
    def __init__(self):
        self.paused_workflows = {}
        self.registered_funcs = {}
        self.socketio_instance = None  # Will be injected
        self.app_logger = None       # Will be injected

    def init_app(self, app, socketio_instance):
        self.socketio_instance = socketio_instance
        self.app_logger = app.logger  # Use the Flask app's logger
        self.app_logger.info("WorkflowManager initialized with app and socketio.")

    # --- DECORATOR ---
    def register_workflow(self, display_name=None, description=None):
        def decorator(func):
            # Ensure manager is initialized before decorators run effectively
            if not self.app_logger:
                # This is a fallback, ideally init_app is called before module import
                print("CRITICAL: WorkflowManager not fully initialized when registering. Logger might be unavailable.")
                # You could raise an error or use a default logger
                # logging.getLogger(__name__).warning("WorkflowManager.register_workflow called before init_app")


            workflow_name = func.__name__
            actual_display_name = display_name or workflow_name.replace('_', ' ').title()
            actual_description = description or func.__doc__ or "No description available."

            @functools.wraps(func)
            def wrapper(main_input=None, *args, **kwargs):
                if not self.socketio_instance or not self.app_logger:
                    print(f"ERROR: WorkflowManager not initialized. Cannot start workflow '{workflow_name}'.")
                    # Potentially raise an error or return a failure indicator
                    return None # Or handle error appropriately

                self.app_logger.info(f"Wrapper called for workflow: {workflow_name}")
                session_id = session.get('session_id')
                if not session_id:
                    session_id = str(uuid.uuid4())
                    session['session_id'] = session_id

                workflow_instance_id = str(uuid.uuid4())
                active_workflows[workflow_instance_id] = {
                    'workflow_name': workflow_name,
                    'session_id': session_id,
                    'original_function': func,
                    'main_input': main_input,
                    'args': args, 'kwargs': kwargs,
                    'paused': False, 'context': {}
                }
                
                self.socketio_instance.start_background_task(self._execute_workflow, workflow_instance_id)
                return workflow_instance_id

            self.registered_funcs[workflow_name] = {
                'id': workflow_name, 'name': actual_display_name,
                'description': actual_description, 'callable_wrapper': wrapper
            }
            if self.app_logger:
                self.app_logger.info(f"Workflow '{workflow_name}' registered as '{actual_display_name}'.")
            else: # Fallback if logger not ready (should not happen with correct init order)
                print(f"INFO (fallback): Workflow '{workflow_name}' registered as '{actual_display_name}'.")
            return wrapper
        return decorator

    # --- EXECUTION & COMMUNICATION METHODS (use self.socketio_instance and self.app_logger) ---
    def _execute_workflow(self, workflow_instance_id):
        workflow_data = active_workflows.get(workflow_instance_id)
        if not workflow_data:
            self.app_logger.error(f"Workflow instance {workflow_instance_id} not found for execution.")
            return

        try:
            progress_fn = lambda title, content: self._send_progress(workflow_instance_id, title, content)
            interact_fn = lambda form_config: self._request_interaction(workflow_instance_id, form_config)
            
            exec_kwargs = workflow_data['kwargs'].copy()
            exec_kwargs['main_input'] = workflow_data['main_input']
            exec_kwargs['progress'] = progress_fn
            exec_kwargs['interact'] = interact_fn
            
            result = workflow_data['original_function'](*workflow_data['args'], **exec_kwargs)
            
            self.socketio_instance.emit('workflow_complete', {
                'workflow_instance_id': workflow_instance_id,
                'workflow_name': workflow_data['workflow_name'], 'result': result
            }, room=workflow_data['session_id'])
            
        except Exception as e:
            self.app_logger.error(f"Error in workflow {workflow_data['workflow_name']} ({workflow_instance_id}): {e}", exc_info=True)
            self.socketio_instance.emit('workflow_error', {
                'workflow_instance_id': workflow_instance_id,
                'workflow_name': workflow_data['workflow_name'], 'error': str(e)
            }, room=workflow_data['session_id'])
        finally:
            if workflow_instance_id in active_workflows: del active_workflows[workflow_instance_id]
            if workflow_instance_id in self.paused_workflows: del self.paused_workflows[workflow_instance_id]

    def _send_progress(self, workflow_instance_id, title, body_content):
        workflow_data = active_workflows.get(workflow_instance_id)
        if workflow_data and self.socketio_instance:
            payload = {
                "action": "status_message", "category": "workflow_progress",
                "message": {"title": title, "body": body_content},
                "workflow_instance_id": workflow_instance_id,
                "workflow_name": workflow_data['workflow_name'], "timestamp": time.time()
            }
            self.socketio_instance.emit('progress_update', payload, room=workflow_data['session_id'])
            self.socketio_instance.sleep(0.1)

    def _request_interaction(self, workflow_instance_id, form_config):
        workflow_data = active_workflows.get(workflow_instance_id)
        if not workflow_data or not self.socketio_instance:
            if self.app_logger: self.app_logger.error(f"Cannot request interaction for non-existent/uninitialized workflow {workflow_instance_id}")
            return None
        
        workflow_data['paused'] = True
        payload = {
            "action": "interaction_request", "category": "workflow_interaction",
            "message": {"title": form_config.get("title", "User Input Required")},
            "form_config": form_config, "workflow_instance_id": workflow_instance_id,
            "workflow_name": workflow_data['workflow_name'], "timestamp": time.time()
        }
        self.paused_workflows[workflow_instance_id] = workflow_data
        self.socketio_instance.emit('interaction_request', payload, room=workflow_data['session_id'])
        
        while workflow_data.get('paused', False):
            self.socketio_instance.sleep(0.5)
        return workflow_data.get('user_response')

    def resume_workflow(self, workflow_instance_id, user_response):
        workflow_data = self.paused_workflows.get(workflow_instance_id)
        if workflow_data and workflow_data.get('paused', False):
            workflow_data['user_response'] = user_response
            workflow_data['paused'] = False
            del self.paused_workflows[workflow_instance_id]
            return True
        if self.app_logger: self.app_logger.warning(f"Failed to resume workflow: {workflow_instance_id}. Not found or not paused.")
        return False

    def get_available_workflows_for_api(self):
        if self.app_logger: self.app_logger.info(f"Getting available workflows. Registered: {list(self.registered_funcs.keys())}")
        return [
            {"id": wf_details["id"], "name": wf_details["name"], "description": wf_details["description"]}
            for wf_name, wf_details in self.registered_funcs.items()
        ]

# --- App Initialization Sequence ---
# 1. Create Flask App
app = Flask(__name__)
app.secret_key = 'your_very_secret_key_CHANGE_ME' # Important: Change this!

# 2. Create WorkflowManager instance
workflow_manager = WorkflowManager()

# 3. Create SocketIO instance and initialize it with the app
socketio = SocketIO(app)

# 4. Initialize WorkflowManager with the app and socketio instance
# This is CRUCIAL: workflow_manager needs app.logger and the socketio instance.
workflow_manager.init_app(app, socketio)

# 5. Now, import the workflows module. Decorators in workflows.py will use the initialized workflow_manager.
app.logger.info("Attempting to import 'workflows' module...")
try:
    import workflows  # Assumes workflows.py is in the same directory orPYTHONPATH
    app.logger.info(f"'workflows' module imported. Current registered functions: {list(workflow_manager.
    registered_funcs.keys())}")
except ImportError as e:
    app.logger.error(f"Failed to import 'workflows' module: {e}. Make sure workflows.py exists and is accessible.")
except Exception as e: # Catch any other error during import (e.g. syntax error in workflows.py)
    app.logger.error(f"An error occurred during 'workflows' module import: {e}", exc_info=True)


# Store for active workflow instances (already defined globally earlier, ensure it's used consistently)
active_workflows = {} # This should be fine as is.


# --- Flask Routes (use `app.logger` and `socketio` instance) ---
@app.route('/')
def index():
    #return render_template('index.html')
    available_wfs = workflow_manager.get_available_workflows_for_api()
    app.logger.info(f"available_wfs within index(): {available_wfs}")
    return render_template('index.html', workflows=available_wfs)

@app.route('/api/workflows', methods=['GET'])
def get_workflows_api():
    app.logger.info("Request received for /api/workflows")
    available_wfs = workflow_manager.get_available_workflows_for_api()
    app.logger.info(f"Responding to /api/workflows with: {available_wfs}")
    return jsonify(available_wfs)

@app.route('/workflows', methods=['POST'])
def start_workflow_route():
    # ... (rest of the route definition, ensure it uses app.logger)
    workflow_id_from_user = request.form.get('workflow_id')
    main_input_text = request.form.get('main_input_text', '')
    app.logger.info(f"Request to start workflow: {workflow_id_from_user} with input: '{main_input_text[:50]}...'")


    workflow_details = workflow_manager.registered_funcs.get(workflow_id_from_user)
    if not workflow_details:
        app.logger.error(f"Workflow not found: {workflow_id_from_user}")
        return jsonify({'status': 'error', 'message': 'Workflow not found'}), 404

    callable_wrapper = workflow_details['callable_wrapper']
    try:
        workflow_instance_id = callable_wrapper(main_input=main_input_text)
        if workflow_instance_id is None: # Check if wrapper indicated an initialization error
             app.logger.error(f"Workflow wrapper for {workflow_id_from_user} returned None. Manager might not be initialized.")
             return jsonify({'status': 'error', 'message': 'Workflow could not be started due to server misconfiguration.'}), 500
        app.logger.info(f"Workflow {workflow_id_from_user} started with instance ID: {workflow_instance_id}")
        return jsonify({'status': 'success', 'workflow_instance_id': workflow_instance_id})
    except Exception as e:
        app.logger.error(f"Failed to start workflow {workflow_id_from_user}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Error starting workflow: {str(e)}'}), 500


# --- SocketIO Event Handlers (use `socketio` instance for decorators, `emit` is fine) ---
@socketio.on('connect')
def handle_connect():
    # ... (rest of the handler, ensure it uses app.logger)
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    emit('connected', {'session_id': session['session_id'], 'sid': request.sid})
    app.logger.info(f"Client connected: sid={request.sid}, session_id={session['session_id']}")


@socketio.on('disconnect')
def handle_disconnect():
    # ... (rest of the handler)
    app.logger.info(f"Client disconnected: sid={request.sid}")

@socketio.on('submit_interaction')
def handle_interaction_submission(data):
    # ... (rest of the handler, ensure it uses app.logger)
    workflow_instance_id = data.get('workflow_instance_id')
    form_data = data.get('form_data')
    app.logger.info(f"Interaction submitted for {workflow_instance_id} with data: {form_data}")

    success = workflow_manager.resume_workflow(workflow_instance_id, form_data)
    
    if success:
        emit('interaction_processed', {
            'workflow_instance_id': workflow_instance_id,
            'message': 'Interaction processed, workflow continues.'
        }, room=session.get('session_id'))
    else:
        emit('interaction_error', {
            'workflow_instance_id': workflow_instance_id,
            'message': 'Failed to process interaction. Workflow not found or not paused.'
        }, room=session.get('session_id'))

# --- Main Execution ---
if __name__ == '__main__':
    app.logger.info("Starting Flask-SocketIO development server...")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)