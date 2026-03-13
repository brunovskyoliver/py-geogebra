import tkinter as tk
import json
import os
import socket
import subprocess
import tempfile
import time

from .tools.language import set_language
from .tools.widgets import Widgets
from .ui.menu_bar import menu
from .ui.toolbar import toolbar
from .config import __version__
from .tools.objects import Objects
from .ui.axes import Axes
from py_geogebra.motions import motions
from . import state
from .ui.sidebar import Sidebar
from . import globals
from .tools.auth0_handler import Auth0Handler
from .flask.app import app
from .motions.changing_screen_size import changing_screen_size
import threading
import sys


RELOAD_SCENE_ENV = "PY_GEOGEBRA_RELOAD_SCENE"

def is_exe():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def _wait_for_port(host: str, port: int, retries: int = 20, delay_sec: float = 0.25) -> bool:
    for _ in range(retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                return True
            except OSError:
                time.sleep(delay_sec)
    return False

def run_flask():
    host = "127.0.0.1"
    port = 5000
    if not _wait_for_port(host, port):
        globals.logger.warning(
            "Flask helper server not started (port 5000 is already in use)."
        )
        return
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except OSError as ex:
        globals.logger.warning(f"Flask helper server failed to start: {ex}")


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _iter_python_files(project_root):
    skip_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "dist",
        "build",
    }
    for current_root, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(".py"):
                yield os.path.join(current_root, filename)


def restore_scene_after_reload(root):
    scene_path = os.environ.pop(RELOAD_SCENE_ENV, "")
    if not scene_path:
        return
    if not os.path.exists(scene_path):
        globals.logger.warning(f"Hot reload scene not found: {scene_path}")
        return
    try:
        with open(scene_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        globals.objects.load_from_dict(root, data)
        changing_screen_size(root)

        def refresh_scene():
            root.update_idletasks()
            globals.objects.refresh()
            if globals.axes:
                globals.axes.update()

        root.after(0, refresh_scene)
        root.after(60, refresh_scene)
        root.after(180, refresh_scene)
        globals.logger.info("Hot reload scene restored.")
    except Exception as ex:
        globals.logger.error(f"Hot reload scene restore failed: {ex}")


def start_hot_reload(root, args):
    if is_exe() or "nohotreload" in args:
        return

    project_root = _project_root()
    mtimes = {}
    for path in _iter_python_files(project_root):
        try:
            mtimes[path] = os.path.getmtime(path)
        except OSError:
            continue

    pending_changed = set()
    last_change_ts = 0.0
    debounce_sec = 0.7
    poll_ms = 800
    reload_in_progress = {"value": False}

    scene_path = os.path.join(tempfile.gettempdir(), "py_geogebra_hot_reload_scene.json")
    globals.logger.info("Hot reload enabled")

    def attempt_reload(changed_paths):
        compile_cmd = [sys.executable, "-m", "py_compile", *changed_paths]
        check = subprocess.run(compile_cmd, capture_output=True, text=True)
        if check.returncode != 0:
            stderr = check.stderr.strip() or check.stdout.strip() or "Unknown compile error"
            globals.logger.error(f"Hot reload skipped (syntax/import error): {stderr}")
            return

        try:
            globals.objects.to_json(scene_path)
        except Exception as ex:
            globals.logger.error(f"Hot reload skipped (scene save failed): {ex}")
            return

        reload_in_progress["value"] = True
        os.environ[RELOAD_SCENE_ENV] = scene_path
        globals.logger.info(f"Hot reloading ({len(changed_paths)} file(s))...")
        os.execv(sys.executable, [sys.executable, *sys.argv])

    def poll():
        nonlocal last_change_ts
        if reload_in_progress["value"]:
            return

        current_files = set()
        for path in _iter_python_files(project_root):
            current_files.add(path)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            old_mtime = mtimes.get(path)
            if old_mtime is None:
                mtimes[path] = mtime
                pending_changed.add(path)
                last_change_ts = time.time()
            elif mtime > old_mtime:
                mtimes[path] = mtime
                pending_changed.add(path)
                last_change_ts = time.time()

        removed = [p for p in list(mtimes.keys()) if p not in current_files]
        for path in removed:
            mtimes.pop(path, None)

        if pending_changed and (time.time() - last_change_ts) >= debounce_sec:
            changed = sorted(pending_changed)
            pending_changed.clear()
            attempt_reload(changed)
            return

        root.after(poll_ms, poll)

    root.after(poll_ms, poll)



def run_app(args):
    global widgets
    set_language("sk")
    widgets = Widgets()
    globals.widgets = widgets
    if not "noserver" in args:
        flask_process = threading.Thread(target=run_flask, daemon=True)
        flask_process.start()
    auth = Auth0Handler()
    globals.auth = auth
    root = tk.Tk()
    globals.root = root
    root.geometry("1280x720")
    widgets.register(lambda: root.title(_("Geogebra ale lepsia") + f" v{__version__}"))

    main_area = tk.Frame(root)
    sidebar = Sidebar(root, main_area)
    globals.sidebar = sidebar
    canvas = tk.Canvas(main_area, background="white")
    globals.canvas = canvas
    objects = Objects()
    globals.objects = objects
    tool_bar = toolbar(root)
    tool_bar.pack(side="top", fill="x")
    main_area.pack(side="top", fill="both", expand=True)
    sidebar.canvas.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    root.update_idletasks()
    state.center = (
        canvas.winfo_width() // 2 + objects.offset_x,
        canvas.winfo_height() // 2 + objects.offset_y,
    )

    axes = Axes(root, objects.unit_size)
    globals.axes = axes
    objects.register(axes)
    motions.bind_all(root)
    canvas.focus_set()
    menu_bar = menu(root, widgets)
    root.config(menu=menu_bar)
    state.shift_pressed = False

    restore_scene_after_reload(root)
    start_hot_reload(root, args)



    root.mainloop()
