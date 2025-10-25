from flask import Flask, render_template, jsonify
from libsql_client import create_client_sync
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN
from ..tools.utils import handle_auth

app = Flask(__name__)

@app.route("/scenes")
def scenes():
    user_info = handle_auth()
    if user_info is None:
        return jsonify({"error":"Auth Error"}), 401
    client = create_client_sync(url = TURSO_URL, auth_token = TURSO_AUTH_TOKEN)
    res = client.execute("SELECT name FROM scenes WHERE user_id = ?", (user_info["sub"],))
    scenes_list = [r["name"] for r in res.rows]
    return render_template("scenes.html", len=len(scenes_list), l=scenes_list)
