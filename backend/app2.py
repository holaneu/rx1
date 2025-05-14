# REMOVE - use app.py instead

from flask import Flask, render_template, request, jsonify, Response
import uuid
import json
import queue
from flask_cors import CORS
from dotenv import load_dotenv
import os

from workflows import workflow
from utils import init_status_queues, make_sse_response

app = Flask(__name__, static_folder='static', template_folder='templates')

# Enable CORS for API routes only
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Secret Keys
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# In-memory stores for this example
task_gens: dict[str, any] = {}
status_queues: dict[str, queue.Queue] = {}

# Inject the shared queue dict into utils
init_status_queues(status_queues)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/start", methods=["POST"])
def start():
    task_id = str(uuid.uuid4())
    status_queues[task_id] = queue.Queue()
    gen = workflow(task_id)
    task_gens[task_id] = gen
    # Kick off the generator until first yield
    msg = next(gen)
    return jsonify({"task_id": task_id, **msg})

@app.route("/continue", methods=["POST"])
def cont():
    body = request.json
    task_id = body.get("task_id")
    gen = task_gens.get(task_id)

    if not gen:
        return jsonify({"error": "unknown task_id"}), 404

    try:
        msg = gen.send(body.get("user_input"))
        return jsonify(msg)
    except StopIteration as e:
        # Signal SSE stream to close
        status_queues[task_id].put(None)
        task_gens.pop(task_id, None)
        return jsonify({"action": "done", "result": getattr(e, "value", None)})

@app.route("/status/stream")
def status_stream():
    task_id = request.args.get("task_id")
    return make_sse_response(task_id)

# --- API routes can go below ---
@app.route('/api/tools/test', methods=['POST'])
def test():
    data = request.json
    return jsonify({"data": data.get("message", "")})

if __name__ == '__main__':
    app.run(port=5005, debug=True)
