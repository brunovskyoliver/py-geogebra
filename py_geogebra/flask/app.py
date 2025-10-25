from flask import Flask, render_template, jsonify
from libsql_client import create_client_sync
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN
from ..tools.utils import handle_auth
import json
from .. import globals
import threading

app = Flask(__name__)

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
    threading.Thread(
        target=lambda: globals.objects.load_scene_from_server(globals.root, name),
        daemon=True
    ).start()
    return jsonify({"status": "ok"})
