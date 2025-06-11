from flask import Flask, render_template, request, jsonify, Response
import uuid
import json
import queue
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time

#from workflows import WORKFLOWS_REGISTRY
from workflows_module.registry import WORKFLOWS_REGISTRY2
from shared import status_queues
from response_types import response_output_error, response_output_success, response_output, ResponseAction, ResponseKey


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
generators: dict[str, any] = {}

# Workflows registry
wf_registry = WORKFLOWS_REGISTRY2


# Routes
@app.route('/')
def page_index():
    return render_template('index.html', workflows=wf_registry)

@app.route('/workflows')
def page_workflows():
    return render_template('workflows.html', workflows=wf_registry)

@app.route('/test')
def page_test():
    return render_template('test.html')

@app.route("/start_task", methods=["POST"])
def start_task():
    try:
        import inspect
        task_id = str(uuid.uuid4())
        data = request.json
        if not data or 'workflow_id' not in data:
            return jsonify(response_output_error({
                ResponseKey.ERROR: "workflow_id is required",
                ResponseKey.TASK_ID: task_id
                })), 400
        workflow_id = data.get('workflow_id')
        workflow = wf_registry.get(workflow_id)
        if not workflow:
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
        generators[task_id] = generator_func
        
        #response_from_generator = next(generator_func)

        # Check if the result is a generator
        if hasattr(generator_func, '__iter__') and hasattr(generator_func, '__next__'):
            # Kick off the generator until first yield
            response_from_generator = next(generator_func)
        else:
            # If it's not a generator, use the return value directly
            response_from_generator = generator_func
        return jsonify({"task_id": task_id, "timestamp": time.time(), **response_from_generator})        
    except Exception as e:
        return jsonify(response_output_error({ResponseKey.ERROR: str(e)})), 500
    

@app.route("/continue_task", methods=["POST"])
def continue_task():
    data = request.json
    task_id = data.get("task_id")
    generator_func = generators.get(task_id)
    if not generator_func:
        return jsonify(response_output_error({ResponseKey.ERROR: "unknown task_id"})), 400
    try:
        continue_generator = generator_func.send(data.get("user_input")) # .send() will resume the generator
        return jsonify(continue_generator)
    except StopIteration as e:
        # Signal SSE stream to close
        status_queues[task_id].put(None)
        generators.pop(task_id, None)        
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
        input_message = data.get("message", "")
        if not input_message:
            return jsonify(response_output_error({ResponseKey.DATA: "No input"}))
        return jsonify(response_output_success({ResponseKey.DATA: input_message + " - from test endpoint"}))
    except Exception as e:
        return jsonify(response_output_error({ResponseKey.ERROR: str(e)})), 500
    

if __name__ == '__main__':
    app.run(port=5005, debug=True)
