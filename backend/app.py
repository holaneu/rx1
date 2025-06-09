from flask import Flask, render_template, request, jsonify, Response
import uuid
import json
import queue
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time

from workflows import WORKFLOWS_REGISTRY
from shared import status_queues
from response_types import response_output, response_output_error, response_output_success, error_response, ResponseAction, ResponseStatus, ResponseKey


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
genenerators: dict[str, any] = {}


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
            #return jsonify(error_response(error="workflow_id is required")), 400
            return jsonify(response_output_error({
                ResponseKey.ERROR: "workflow_id is required",
                ResponseKey.TASK_ID: task_id
                })), 400
        workflow_id = data.get('workflow_id')
        workflow = WORKFLOWS_REGISTRY.get(workflow_id)
        if not workflow:
            #return jsonify({'error': 'Invalid workflow'}), 400
            #return jsonify(error_response(error="Invalid workflow")), 400
            return jsonify(response_output_error({
                ResponseKey.ERROR: "Invalid workflow",
                ResponseKey.TASK_ID: task_id
                })), 400            
        workflow_func_params = inspect.signature(workflow['function']).parameters
        # Build kwargs based on required parameters
        kwargs = {}
        if 'input' in workflow_func_params:
            input_text = data.get('input')
            if input_text is None:
                #return jsonify({'error': 'Missing required input'}), 400
                #return jsonify(error_response(error="Missing required input")), 400
                return jsonify(response_output_error({
                    ResponseKey.ERROR: "Missing required input",
                    ResponseKey.TASK_ID: task_id
                    })), 400
            kwargs['input'] = input_text
        if 'model' in workflow_func_params:
            kwargs['model'] = workflow['model']
        if 'task_id' in workflow_func_params:
            kwargs['task_id'] = task_id

        status_queues[task_id] = queue.Queue()
        generator_func = workflow['function'](**kwargs)
        genenerators[task_id] = generator_func
        # Kick off the generator until first yield
        response_from_generator = next(generator_func)
        return jsonify({"task_id": task_id, "timestamp": time.time(), **response_from_generator})
        """return jsonify(success_response(
            data={"task_id": task_id},
            **msg
        ))"""
    except Exception as e:
        #return jsonify(error_response(str(e))), 500
        return jsonify(response_output_error({ResponseKey.ERROR: str(e)})), 500
    

@app.route("/continue_task", methods=["POST"])
def continue_task():
    data = request.json
    task_id = data.get("task_id")
    generator_func = genenerators.get(task_id)
    if not generator_func:
        #return jsonify({"error": "unknown task_id"}), 404
        #return jsonify(error_response(error="unknown task_id")), 400
        return jsonify(response_output_error({ResponseKey.ERROR: "unknown task_id"})), 400
    try:
        continue_generator = generator_func.send(data.get("user_input")) # .send() will resume the generator
        return jsonify(continue_generator)
    except StopIteration as e:
        # Signal SSE stream to close
        status_queues[task_id].put(None)
        genenerators.pop(task_id, None)
        #return jsonify({"action": "done", "result": getattr(e, "value", None), "task_id": task_id})
        #return jsonify({"action": "task_done", "category": "workflow", "message": {"title": "Workflow finished", "body": getattr(e, "value", None)}, "task_id": task_id, "timestamp": time.time()})
        """return jsonify(success_response(
            data=getattr(e, "value", None),
            action=ResponseAction.WORKFLOW_FINISHED,
            message=ResponseMessage(
                title="Workflow finished",
                body=getattr(e, "value", None)
            ),
            task_id=task_id
        ))"""
        return jsonify(getattr(e, "value", None) or {})


@app.route("/msg/stream")
def status_stream():
    task_id = request.args.get("task_id")
    task_status_queue = status_queues.get(task_id) # Get the queue for this task_id
    if not task_status_queue:
        return "", 404
    def event_stream():
        while True:
            task_status_item = task_status_queue.get() # block until next status or None
            if task_status_item is None:
                break # generator finished
            payload = response_output_success({
                ResponseKey.ACTION: ResponseAction.STATUS_MESSAGE, 
                ResponseKey.CATEGORY: "workflow", 
                **task_status_item
                })
            yield f"data: {json.dumps(payload)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")


# --- API routes can go below ---
@app.route('/api/tools/test', methods=['POST'])
def test():
    try:
        data = request.json
        payload = response_output_success({
            ResponseKey.DATA: data.get("message", "") + " - from test endpoint"
        })
        return jsonify(payload)
    except Exception as e:
        return jsonify(response_output_error({ResponseKey.ERROR: str(e)})), 500
    

if __name__ == '__main__':
    app.run(port=5005, debug=True)
