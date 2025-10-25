from tkinter import messagebox, filedialog, simpledialog
import sys, json, os
from .. import globals
from libsql_client import create_client_sync
from ..tools.auth_config import TURSO_URL, TURSO_AUTH_TOKEN


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
    from ..tools.auth0_handler import Auth0Handler
    auth = Auth0Handler()
    user_info = auth.get_user_info()
    if not user_info:
        access_token = auth.authenticate()
        if not access_token:
            messagebox.showerror(_("Chyba"), _("Nepodarilo sa authentikovať"))
            return
        user_info = auth.get_user_info()
        if not user_info:
            return
    print(user_info)
    name = simpledialog.askstring(title=_("Zadaj názov scény"), prompt=_("Prosím zadaj názov pre uloženie scény"))
    if name:
        scene = globals.objects.to_dict()
        try:
            client = create_client_sync(url = TURSO_URL, auth_token = TURSO_AUTH_TOKEN)
            client.execute("""
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    name TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nickname, name)
);
        """)
            client.execute(
        "INSERT INTO scenes (nickname, name, data) VALUES (?, ?, ?)",
        (user_info["nickname"], name, json.dumps(scene)))
            client.close()

            messagebox.showinfo(_("OK"), _("Scéna bola uložená"))
        except Exception as e:
            messagebox.showerror(_("Chyba spojenia s DB"), str(e))


