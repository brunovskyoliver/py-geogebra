import os
import sys
from flask import Flask, render_template, jsonify
from libsql_client import create_client_sync
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN
from ..tools.utils import handle_auth
from .. import globals
import json, threading

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

template_dir = os.path.join(base_path, "py_geogebra", "flask", "templates")
static_dir   = os.path.join(base_path, "py_geogebra", "flask", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route("/api/scene/<name>")
def open_scene(name):
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error":"No Access"}), 402
    client = create_client_sync(url = TURSO_URL, auth_token = TURSO_AUTH_TOKEN)
    res = client.execute(
        "SELECT data FROM scenes WHERE user_id = ? AND name = ?",
        (user_info["sub"], name),
    )
    json_data = res.rows[0]["data"]
    return jsonify(json.loads(json_data))

@app.route("/scenes")
def scenes():
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error":"Auth Error"}), 401
    client = create_client_sync(url = TURSO_URL, auth_token = TURSO_AUTH_TOKEN)
    res = client.execute("SELECT name FROM scenes WHERE user_id = ?", (user_info["sub"],))
    scenes_list = [r["name"] for r in res.rows]
    return render_template("scenes.html", len=len(scenes_list), scenes=scenes_list)

@app.route("/load_scene/<name>")
def load_scene(name):
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error":"No Access"}), 402
    threading.Thread(
        target=lambda: globals.objects.load_scene_from_server(globals.root, name),
        daemon=True
    ).start()
    return jsonify({"status": "ok"})
