from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit
import logging
import uuid
from workflows import workflows_registry

# Configure basic logging
logging.basicConfig(level=logging.INFO)

class WorkflowManager:
    def __init__(self):
        self.paused_workflows = {}
        self.active_workflows = {}
        self.socketio_instance = None
        self.app_logger = None

    def init_app(self, app, socketio_instance):
        self.socketio_instance = socketio_instance
        self.app_logger = app.logger
        self.app_logger.info("WorkflowManager initialized with app and socketio.")

    def _execute_workflow(self, workflow_instance_id):
        workflow_data = self.active_workflows.get(workflow_instance_id)
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
                'workflow_name': workflow_data['workflow_name'],
                'result': result
            }, room=workflow_data['session_id'])
            
        except Exception as e:
            self.app_logger.error(f"Error in workflow {workflow_data['workflow_name']}: {e}", exc_info=True)
            self.socketio_instance.emit('workflow_error', {
                'workflow_instance_id': workflow_instance_id,
                'workflow_name': workflow_data['workflow_name'],
                'error': str(e)
            }, room=workflow_data['session_id'])
        finally:
            if workflow_instance_id in self.active_workflows:
                del self.active_workflows[workflow_instance_id]
            if workflow_instance_id in self.paused_workflows:
                del self.paused_workflows[workflow_instance_id]

    def _send_progress(self, workflow_instance_id, title, body_content):
        workflow_data = self.active_workflows.get(workflow_instance_id)
        if workflow_data and self.socketio_instance:
            payload = {
                "action": "status_message",
                "category": "workflow_progress",
                "message": {"title": title, "body": body_content},
                "workflow_instance_id": workflow_instance_id,
                "workflow_name": workflow_data['workflow_name'],
                "timestamp": time.time()
            }
            self.socketio_instance.emit('progress_update', payload, room=workflow_data['session_id'])
            self.socketio_instance.sleep(0.1)

    def _request_interaction(self, workflow_instance_id, form_config):
        workflow_data = self.active_workflows.get(workflow_instance_id)
        if not workflow_data or not self.socketio_instance:
            self.app_logger.error(f"Cannot request interaction for workflow {workflow_instance_id}")
            return None
        
        workflow_data['paused'] = True
        payload = {
            "action": "interaction_request",
            "category": "workflow_interaction",
            "message": {"title": form_config.get("title", "User Input Required")},
            "form_config": form_config,
            "workflow_instance_id": workflow_instance_id,
            "workflow_name": workflow_data['workflow_name'],
            "timestamp": time.time()
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
        self.app_logger.warning(f"Failed to resume workflow: {workflow_instance_id}")
        return False

    def get_available_workflows_for_api(self):
        self.app_logger.info(f"Getting available workflows from registry")
        return [
            {"id": wf_details["id"], "name": wf_details["name"], "description": wf_details["description"]}
            for wf_name, wf_details in workflows_registry.items()
        ]

# App Initialization
app = Flask(__name__)
app.secret_key = 'your_very_secret_key_CHANGE_ME'

workflow_manager = WorkflowManager()
socketio = SocketIO(app)
workflow_manager.init_app(app, socketio)

# Routes
@app.route('/')
def index():
    available_wfs = workflow_manager.get_available_workflows_for_api()
    app.logger.info(f"Available workflows: {available_wfs}")
    return render_template('index.html', workflows=available_wfs)

@app.route('/api/workflows', methods=['GET'])
def get_workflows_api():
    app.logger.info("Request received for /api/workflows")
    available_wfs = workflow_manager.get_available_workflows_for_api()
    return jsonify(available_wfs)

@app.route('/workflows', methods=['POST'])
def start_workflow_route():
    workflow_id = request.form.get('workflow_id')
    main_input_text = request.form.get('main_input_text', '')
    app.logger.info(f"Request to start workflow: {workflow_id}")

    workflow_details = workflows_registry.get(workflow_id)
    if not workflow_details:
        app.logger.error(f"Workflow not found: {workflow_id}")
        return jsonify({'status': 'error', 'message': 'Workflow not found'}), 404

    try:
        workflow_instance_id = workflow_details['callable_wrapper'](
            workflow_manager,
            main_input=main_input_text
        )
        return jsonify({
            'status': 'success',
            'workflow_instance_id': workflow_instance_id
        })
    except Exception as e:
        app.logger.error(f"Failed to start workflow: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Socket.IO Event Handlers
@socketio.on('connect')
def handle_connect():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    emit('connected', {'session_id': session['session_id'], 'sid': request.sid})
    app.logger.info(f"Client connected: sid={request.sid}, session_id={session['session_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info(f"Client disconnected: sid={request.sid}")

@socketio.on('submit_interaction')
def handle_interaction_submission(data):
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
