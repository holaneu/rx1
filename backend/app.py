from flask import Flask, render_template, request, jsonify, Response
import uuid
import json
import queue
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time

from workflows import WORKFLOWS_REGISTRY
from shared import send_status_message, status_queues
from response_types import success_response, error_response, ResponseAction, ResponseMessage


# ----------------------
# Flask app setup

app = Flask(__name__, static_folder='static', template_folder='templates')

# Enable CORS for API routes only
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Secret Keys
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# In‐memory stores for this example
task_gens: dict[str, any] = {}

@app.route('/')
def index():
    return render_template('index.html', workflows=WORKFLOWS_REGISTRY)

@app.route("/start_task", methods=["POST"])
def start_task():
    try:
        import inspect
        task_id = str(uuid.uuid4())
        data = request.json
        if not data or 'workflow_id' not in data:
            #return jsonify({"error": "workflow_id is required"}), 400
            return jsonify(error_response(error="workflow_id is required")), 400
        workflow_id = data.get('workflow_id')
        workflow = WORKFLOWS_REGISTRY.get(workflow_id)
        if not workflow:
            #return jsonify({'error': 'Invalid workflow'}), 400
            return jsonify(error_response(error="Invalid workflow")), 400
        workflow_func_params = inspect.signature(workflow['function']).parameters
        # Build kwargs based on required parameters
        kwargs = {}
        if 'input' in workflow_func_params:
            input_text = data.get('input')
            if input_text is None:
                #return jsonify({'error': 'Missing required input'}), 400
                return jsonify(error_response(error="Missing required input")), 400
            kwargs['input'] = input_text
        if 'model' in workflow_func_params:
            kwargs['model'] = workflow['model']
        if 'task_id' in workflow_func_params:
            kwargs['task_id'] = task_id

        status_queues[task_id] = queue.Queue()
        generator_func = workflow['function'](**kwargs)
        task_gens[task_id] = generator_func
        # Kick off the generator until first yield
        msg = next(generator_func)
        return jsonify({"task_id": task_id, "timestamp": time.time(), **msg})
        """return jsonify(success_response(
            data={"task_id": task_id},
            **msg
        ))"""
    except Exception as e:
        return jsonify(error_response(str(e))), 500
    

@app.route("/continue_task", methods=["POST"])
def continue_task():
    body = request.json
    task_id = body.get("task_id")
    generator_func = task_gens.get(task_id)
    if not generator_func:
        return jsonify({"error": "unknown task_id"}), 404
    try:
        msg = generator_func.send(body.get("user_input"))
        return jsonify(msg)
    except StopIteration as e:
        # Signal SSE stream to close
        status_queues[task_id].put(None)
        task_gens.pop(task_id, None)
        #return jsonify({"action": "done", "result": getattr(e, "value", None), "task_id": task_id})
        return jsonify({"action": "task_done", "category": "workflow", "message": {"title": "Workflow finished", "body": getattr(e, "value", None)}, "task_id": task_id, "timestamp": time.time()})

@app.route("/msg/stream")
def status_stream():
    task_id = request.args.get("task_id")
    q = status_queues.get(task_id)
    if not q:
        return "", 404
    def event_stream():
        while True:
            msg = q.get()          # block until next status or None
            if msg is None:
                break              # generator finished
            payload = {"action": "status_message", "category": "workflow", "message": msg, "task_id": task_id, "timestamp": time.time()}
            yield f"data: {json.dumps(payload)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

# --- API routes can go below ---
@app.route('/api/tools/test', methods=['POST'])
def test():
    data = request.json
    return jsonify({"data": data.get("message", "")})

if __name__ == '__main__':
    app.run(port=5005, debug=True)
