from flask import Flask, render_template, request, jsonify, Response, abort, redirect, url_for
from flask_cors import CORS

import uuid
import json
import queue
from dotenv import load_dotenv
import os
import time
import threading

# REMOVE: from app.workflows.core import WORKFLOWS_REGISTRY
import app.workflows.core as workflows_core
from app.utils.shared import all_task_sse_queues
from app.utils.response_types import response_output_error, response_output_success, ResponseAction, ResponseKey, ResponseStatus
from app.storage.manager import FileStorageManager
from app.configs.app_config import APP_SETTINGS
from app.configs.ai_config import llm_models


# ----------------------
# Testing logs

for k,v in workflows_core.WORKFLOWS_REGISTRY.items():
    print(k, v.get("module"))

# ----------------------
# Flask app setup

app = Flask(__name__, static_folder='app/ui/static', template_folder='app/ui/templates')

# Enable CORS for API routes only
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Secret Keys
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# In‐memory stores for this example
generators: dict[str, any] = {}

# REMOVE?? Workflows registry
# wf_registry = WORKFLOWS_REGISTRY

# File storage manager
FILES_FOLDER = APP_SETTINGS.USER_DATA_PATH
file_manager = FileStorageManager(base_path=FILES_FOLDER, skip_folders=["__pycache__"])

# --- one-per-process global lock ---
# used for reload_modules() API
_init_update_lock = threading.Lock()


@app.template_filter('active_page')
def active_page(current_page, page_name):
    return 'active' if current_page == page_name else ''



# Routes
@app.route('/')
def page_index():
    return render_template('index.html', workflows=workflows_core.WORKFLOWS_REGISTRY)

@app.route('/workflows')
def page_workflows():
    return render_template('workflows.html', workflows=workflows_core.WORKFLOWS_REGISTRY, llm_models=llm_models)

@app.route('/test')
def page_test():
    return render_template('test.html')

@app.route("/msg/stream")
def status_stream():
    task_id = request.args.get("task_id")
    task_status_queue = all_task_sse_queues.get(task_id) # Get the queue for this task_id
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

# redirect to handle the trailing slash issue
@app.route('/files/')
def files_with_slash():
    return redirect(url_for('files'))

@app.route('/files')
@app.route('/files/folder/<item_id>')
def files(item_id=None):
    structure = file_manager.get_structure()
    items_list = structure['items']
    
    # Get current folder and build breadcrumb path
    current_folder = None
    breadcrumbs = []
    
    if item_id:
        current_folder = next((item for item in items_list if item.id == item_id), None)
        if not current_folder or current_folder.type != 'folder':
            abort(404)
            
        # Build breadcrumbs
        temp_folder = current_folder
        while hasattr(temp_folder, 'parent'):
            parent = next((item for item in items_list if item.id == temp_folder.parent), None)
            if parent:
                breadcrumbs.insert(0, parent)
                temp_folder = parent
            else:
                break
        breadcrumbs.append(current_folder)
    
    # Filter items for current folder
    filtered_items = [
        item for item in items_list 
        if (not item_id and not hasattr(item, 'parent')) or
           (hasattr(item, 'parent') and item.parent == item_id)
    ]
    
    return render_template('files.html', 
                         items=filtered_items, 
                         current_folder=current_folder,
                         breadcrumbs=breadcrumbs)


@app.route('/files/file/<item_id>')
def files_file_detail(item_id):
    structure = file_manager.get_structure()
    item = next((item for item in structure['items'] if item.id == item_id), None)
    
    if not item or item.type != 'file':
        abort(404)
    
    # Generate breadcrumbs by traversing up through parent folders
    breadcrumbs = []
    if not hasattr(item, 'parent'):
        # If item has no parent, it's in the root folder
        breadcrumbs = [{'id': None, 'name': 'root', 'type': 'folder'}]
    else:
        current = next((i for i in structure['items'] if i.id == item.parent), None)
        while current:
            breadcrumbs.insert(0, current)
            current = next((i for i in structure['items'] if i.id == current.parent), None) if hasattr(current, 'parent') else None

    try:
        full_path = os.path.join(FILES_FOLDER, item.file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('files_file_detail.html', item=item, content=content, breadcrumbs=breadcrumbs)
    except Exception as e:
        abort(500)


# -------------------------------
# --- API routes ---
# -------------------------------

@app.route("/api/start_task", methods=["POST"])
def start_task():
    try:
        import inspect
        task_id = str(uuid.uuid4())
        all_task_sse_queues[task_id] = queue.Queue()
        data = request.json
        if not data or 'workflow_id' not in data:
            return jsonify(response_output_error({
                ResponseKey.ERROR: "[start_task()]: workflow_id is required. Probably you forgot to select workflow.",
                ResponseKey.TASK_ID: task_id
                })), 400
        workflow_id = data.get('workflow_id')
        workflow = workflows_core.WORKFLOWS_REGISTRY.get(workflow_id)
        if not workflow:
            return jsonify(response_output_error({
                ResponseKey.ERROR: "[start_task()]: Invalid workflow. Workflow not found in workflows registry.",
                ResponseKey.TASK_ID: task_id
                })), 400            
        workflow_func_params = inspect.signature(workflow['function']).parameters
        # Build kwargs based on required parameters
        kwargs = {}
        if 'input' in workflow_func_params:
            user_input = data.get('user_input')
            if user_input is None or user_input.strip() == "":
                return jsonify(response_output_error({
                    ResponseKey.ERROR: "[start_task()]: Missing required input. Selected workflow requires 'input' to be provided.",
                    ResponseKey.TASK_ID: task_id
                    })), 400
            kwargs['input'] = user_input
        
        if 'model' in data and 'model' in workflow_func_params:
            kwargs['model'] = data.get('model')
        # Always include task_id
        kwargs['task_id'] = task_id
                
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
    

@app.route("/api/continue_task", methods=["POST"])
def continue_task():
    data = request.json
    task_id = data.get("task_id")
    generator_func = generators.get(task_id)
    if not generator_func:
        return jsonify(response_output_error({ResponseKey.ERROR: "[continue_task()]: unknown task_id. Probably the workflow func incorrectly works with task_id"})), 400
    try:
        continue_generator = generator_func.send(data.get("user_input")) # .send() will resume the generator
        return jsonify(continue_generator)
    except StopIteration as e:
        # Signal SSE stream to close
        all_task_sse_queues[task_id].put(None)
        generators.pop(task_id, None)        
        return jsonify(getattr(e, "value", None) or {})


@app.route('/api/tools/test', methods=['POST'])
def test():
    try:
        data = request.json
        input_message = data.get("message", "")
        if not input_message:
            return jsonify({
                ResponseKey.STATUS: ResponseStatus.ERROR, 
                ResponseKey.ERROR: "No input",
                ResponseKey.DATA: "No input",
                ResponseKey.MESSAGE: {
                    ResponseKey.TITLE: ResponseStatus.ERROR,
                    ResponseKey.BODY: f"No input"
                } 
            }), 400
        return jsonify({
            ResponseKey.STATUS: ResponseStatus.SUCCESS, 
            ResponseKey.DATA: input_message + " - from test endpoint",
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: ResponseStatus.SUCCESS,
                ResponseKey.BODY: f"Message processed"
            } 
        }), 200
    except Exception as e:
        return jsonify({
            ResponseKey.STATUS: ResponseStatus.ERROR, 
            ResponseKey.ERROR: str(e),
            ResponseKey.MESSAGE: {
                ResponseKey.TITLE: ResponseStatus.ERROR,
                ResponseKey.BODY: f"Error: {str(e)}"
            } 
        }), 500

# RENAME TO get_workflows_registry
@app.get("/api/get_workflows_registry")
def api_get_workflows_registry():
    """Return current workflow registry without function objects."""    
    try:
        workflows = {
            wf_id: {k: v for k, v in wf.items() if k != "function"}
            for wf_id, wf in workflows_core.WORKFLOWS_REGISTRY.items()
        }
        return jsonify({
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.DATA: workflows,
            ResponseKey.MESSAGE: "Workflows registry retrieved successfully.",
        })
    except Exception as e:
        return {
            ResponseKey.STATUS: ResponseStatus.ERROR,
            ResponseKey.ERROR: f"[{__name__}]: {str(e)}.",
            ResponseKey.MESSAGE: f"[{__name__}]: {str(e)}.",
        }

    
@app.route('/api/reload_modules', methods=['POST'])
def reload_modules():
    """Hot-reload all in-package modules, noticing any new files."""
    try:
        import importlib    
        from app.utils.update_init2 import update_inits
        with _init_update_lock:             # blocks concurrent requests
            importlib.invalidate_caches()   # make new .py files visible            
            update_inits("app_dirs")
            update_inits("user_data_extensions_dirs") 
            update_inits("user_data_admin_dirs")
        return {
            ResponseKey.STATUS: ResponseStatus.SUCCESS,
            ResponseKey.MESSAGE: "Modules reloaded.",
        }
    except Exception as e:
        return {
            ResponseKey.STATUS: ResponseStatus.ERROR,
            ResponseKey.ERROR: f"[{__name__}]: {str(e)}.",
            ResponseKey.MESSAGE: f"[{__name__}]: {str(e)}.",
        }

# --- Main entry point ---
if __name__ == '__main__':
    os.makedirs(FILES_FOLDER, exist_ok=True)
    app.run(port=5005, debug=True)
