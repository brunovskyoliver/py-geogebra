import os
import sys
import json
import threading
import libsql
from flask import Flask, render_template, jsonify
from ..tools.utils import handle_auth
from .. import globals
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

template_dir = os.path.join(base_path, "py_geogebra", "flask", "templates")
static_dir = os.path.join(base_path, "py_geogebra", "flask", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

LOCAL_DB = os.path.join(base_path, "local.db")

def get_conn():
    return libsql.connect(LOCAL_DB, sync_url=TURSO_URL, auth_token=TURSO_AUTH_TOKEN)


@app.route("/api/scene/<name>")
def open_scene(name):
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error": "No Access"}), 402
    try:
        conn = get_conn()
        conn.sync()
        cur = conn.cursor()
        cur.execute(
            "SELECT data FROM scenes WHERE user_id = ? AND name = ?",
            (user_info["sub"], name),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Not found"}), 404
        json_data = row[0]
        return jsonify(json.loads(json_data))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/scenes")
def scenes():
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error": "Auth Error"}), 401

    try:
        conn = get_conn()
        conn.sync()
        cur = conn.cursor()
        cur.execute("SELECT name FROM scenes WHERE user_id = ?", (user_info["sub"],))
        scenes_list = [r[0] for r in cur.fetchall()]
        conn.close()
        return render_template("scenes.html", len=len(scenes_list), scenes=scenes_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/load_scene/<name>")
def load_scene(name):
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error": "No Access"}), 402
    threading.Thread(
        target=lambda: globals.objects.load_scene_from_server(globals.root, name),
        daemon=True,
    ).start()

    return jsonify({"status": "ok"})

