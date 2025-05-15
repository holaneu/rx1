{
    "action": "status",
    "message": {
        "title": "Started", 
        "body": "Initializing workflow…"
    }
}

{
    "action": "need_user_input",
    "message": {
        "title": "Started", 
        "body": "Initializing workflow…"
    }
}

@app.route("/api/workflows", methods=["GET"])
def get_workflows():
    return jsonify({
        id: {
            "name": info["name"],
            "description": info["description"],
            "category": info["category"]
        } for id, info in WORKFLOWS_REGISTRY.items()
    })
    
    
@app.route("/start", methods=["POST"])
def start():
    body = request.json
    workflow_id = body.get("workflow_id")
    
    if not workflow_id or workflow_id not in WORKFLOWS_REGISTRY:
        return jsonify({"error": "invalid or missing workflow_id"}), 400
        
    workflow = WORKFLOWS_REGISTRY[workflow_id]["function"]
    task_id = str(uuid.uuid4())
    status_queues[task_id] = queue.Queue()
    gen = workflow(task_id)
    task_gens[task_id] = gen

    # Kick off the generator until first yield
    msg = next(gen)
    return jsonify({"task_id": task_id, **msg})

