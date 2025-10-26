from tkinter import messagebox, filedialog, simpledialog
import sys, json, os

from py_geogebra.tools.utils import handle_auth
from .. import globals
from libsql_client import create_client_sync
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN
import webbrowser


def ask_for_update(widgets):
    ask = messagebox.askyesno(
        title=_("Dostupná aktualizácia"),
        message=_("Chcete nainštalovať najnovšiu verziu?"),
    )
    return ask


def no_need_to_update():
    messagebox.showinfo(
        title=_("Žiadna dostupná aktualizácia"), message=_("Si na najnovšej verzii")
    )


def ran_from_python(filepath):
    messagebox.showinfo(
        title=_("Nespustil si binary"), message=_(f"Binary nájdeš v {filepath}")
    )


def open_from_file(root):
    if getattr(
        sys, "frozen", False
    ):  # https://pyinstaller.org/en/stable/runtime-information.html
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    file = filedialog.askopenfile(defaultextension="json", initialdir=base_path)
    if file:
        data = json.load(file)
        globals.objects.load_from_dict(root, data)


def save_file(root):
    if getattr(
        sys, "frozen", False
    ):  # https://pyinstaller.org/en/stable/runtime-information.html
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    file = filedialog.asksaveasfilename(defaultextension="json", initialdir=base_path)
    if file:
        globals.objects.to_json(file)

def save_db(root):
    import ssl
    ssl_context = ssl._create_unverified_context()
    user_info = handle_auth()
    if user_info is None:
        return
    name = simpledialog.askstring(title=_("Zadaj názov scény"), prompt=_("Prosím zadaj názov pre uloženie scény"))
    if name:
        scene = globals.objects.to_dict()
        try:
            client = create_client_sync(url = TURSO_URL, auth_token = TURSO_AUTH_TOKEN, ssl=ssl_context)
#             client.execute("""
# CREATE TABLE IF NOT EXISTS scenes (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id TEXT NOT NULL,
#     nickname TEXT NOT NULL,
#     name TEXT NOT NULL,
#     data TEXT NOT NULL,
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE(user_id, name)
# );
#         """)
            client.execute(
        "INSERT INTO scenes (user_id, nickname, name, data) VALUES (?,?, ?, ?)",
        (user_info["sub"], user_info["nickname"], name, json.dumps(scene)))
            client.close()

            messagebox.showinfo(_("OK"), _("Scéna bola uložená"))
        except Exception as e:
            messagebox.showerror(_("Chyba spojenia s DB"), str(e))

def load_db(root):
    webbrowser.open("http://127.0.0.1:5000/scenes")

