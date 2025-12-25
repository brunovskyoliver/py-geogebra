import requests
import tempfile
import platform
import shutil
import os
import tarfile
import subprocess
import sys
from ..config import __version__
from ..ui.dialogs import no_need_to_update, ran_from_python


url = "https://api.github.com/repos/brunovskyoliver/py-geogebra/releases/latest"
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
assets_headers = {
    "Accept": "application/octet-stream",
    "X-GitHub-Api-Version": "2022-11-28",
}


# https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28
def check_version():
    response = requests.get(url=url, headers=headers, timeout=5)
    response.raise_for_status()
    return response.json()["tag_name"].replace("v", "")

def windows_launcher_path():
    return os.path.join(get_dir(), "py-geogebra-launcher.exe")


def download_latest(filename: str):
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    res_json = response.json()
    asset = None
    for a in res_json["assets"]:
        if a["name"] == filename:
            asset = a
            break
    if asset is None:
        raise RuntimeError(f"Takyto subor nemame: {filename}")

    download_url = asset["url"]
    download_file = requests.get(url=download_url, stream=True, headers=assets_headers)
    download_file.raise_for_status()
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(tmp_path, "wb") as tmp_file:
        shutil.copyfileobj(download_file.raw, tmp_file)

    return tmp_path


def unpack_tarball(tar_file):
    tmp_dir = tempfile.mkdtemp(prefix="py-geogebra-")
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(tmp_dir)
    for root, _, files in os.walk(tmp_dir):
        for f in files:
            bin_path = os.path.join(root, f)
            os.chmod(bin_path, 0o755)
            return bin_path
    raise RuntimeError(f"Nenasli sme binary v dir {tmp_dir}")


def get_dir():
    if platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Application Support/PyGeogebra")
    elif platform.system() == "Linux":
        return os.path.expanduser("~/.local/share/pygeogebra")
    else:
        return os.path.join(os.getenv("LOCALAPPDATA"), "PyGeogebra")


def find_dir():
    app_dir = get_dir()
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def curr_loc():
    if getattr(sys, "frozen", False):
        return sys.executable
    return None


def init(binary_path, version):
    app_dir = find_dir()
    version_dir = os.path.join(app_dir, f"v{version}")
    os.makedirs(version_dir, exist_ok=True)

    bin_name = os.path.basename(binary_path)
    new_bin_path = os.path.join(version_dir, bin_name)

    if not os.path.exists(new_bin_path):
        shutil.copy2(binary_path, new_bin_path)
        os.chmod(new_bin_path, 0o755)

    return new_bin_path


def install_new(bin_path):
    app_dir = find_dir()
    version = check_version()

    version_dir = os.path.join(app_dir, f"v{version}")
    os.makedirs(version_dir, exist_ok=True)

    bin_name = os.path.basename(bin_path)
    new_bin_path = os.path.join(version_dir, bin_name)
    shutil.copy2(bin_path, new_bin_path)
    os.chmod(new_bin_path, 0o755)

    return new_bin_path


def create_launcher(replace_original=False):
    system = platform.system()

    if system == "Windows":
        return windows_launcher_path()

    app_dir = get_dir()
    current_location = curr_loc()

    launcher_path = (
        current_location + ".sh"
        if current_location and not current_location.endswith(".sh")
        else os.path.expanduser("~/Applications/pygeogebra")
    )

    content = f"""#!/bin/bash
APP_DIR="{app_dir}"
LATEST=$(ls -v "$APP_DIR" | grep "^v" | tail -n 1)
[ -z "$LATEST" ] && exit 1
BINARY=$(ls "$APP_DIR/$LATEST" | grep "py-geogebra")
exec "$APP_DIR/$LATEST/$BINARY" "$@"
"""

    with open(launcher_path, "w") as f:
        f.write(content)

    os.chmod(launcher_path, 0o755)
    return launcher_path

def restart_process(binary_path):
    new_binary_path = install_new(binary_path)

    if platform.system() == "Windows":
        launcher = windows_launcher_path()
        subprocess.Popen([launcher], close_fds=True)
        os._exit(0)
    else:
        launcher = create_launcher(replace_original=True)
        subprocess.Popen([launcher])
        os._exit(0)

    sys.exit(0)


def handle_version(root, widgets, ask_for_update):
    current_location = curr_loc()
    if current_location and not os.path.exists(get_dir()):
        init(current_location, __version__)
        launcher_path = create_launcher(replace_original=True)

    local_version = __version__
    servers_version = check_version()
    is_tar = False
    assert len(servers_version) > 0
    if local_version != servers_version:
        if ask_for_update(widgets):
            os_name = platform.system().lower()
            if "darwin" in os_name:
                filename = "py-geogebra-darwin.tar.gz"
                is_tar = True
            elif "linux" in os_name:
                filename = "py-geogebra-linux.tar.gz"
                is_tar = True
            elif "windows" in os_name:
                filename = "py-geogebra-windows.exe"
            else:
                raise RuntimeError(f"Zatial nepodporujeme {os_name}")

            tmp_file = download_latest(filename)
            if is_tar:
                unpacked_binary = unpack_tarball(tmp_file)
            else:
                unpacked_binary = tmp_file

            if getattr(sys, "frozen", False):
                restart_process(unpacked_binary)
            else:
                ran_from_python(unpacked_binary)

        else:
            pass
    else:
        no_need_to_update()
