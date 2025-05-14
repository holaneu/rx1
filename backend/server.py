# backend/server.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Enable CORS for API routes only
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Secret Keys
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# --- Example route to serve frontend ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API routes can go below ---
@app.route('/api/tools/echo', methods=['POST'])
def echo_tool():
    data = request.json
    return jsonify({"echo": data.get("message", "")})

@app.route('/api/tools/test', methods=['POST'])
def test():
    data = request.json
    return jsonify({"data": data.get("message", "")})

# Add other tool, assistant, workflow routes here later

if __name__ == '__main__':
    app.run(port=5005, debug=True)
