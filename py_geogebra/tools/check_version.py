import requests
import tempfile
import platform
import shutil
import os
import tarfile
import subprocess
import sys
from ..tools.version import __version__
from ..ui.dialogs import ask_for_update, no_need_to_update, ran_from_python


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


def restart_process(binary_path):
    current_binary = sys.executable
    backup = current_binary + ".bak"
    shutil.move(current_binary, backup)
    shutil.copy2(binary_path, current_binary)
    os.chmod(current_binary, 0o755)
    subprocess.Popen([current_binary])
    sys.exit(0)


def handle_version(root, widgets, ask_for_update):
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
                print(f"Stiahli sme binary do {unpacked_binary}")
            else:
                unpacked_binary = tmp_file
                print(f"Stiahli sme binary do {tmp_file}")

            if getattr(sys, "frozen", False):
                restart_process(unpacked_binary)
            else:
                ran_from_python(unpacked_binary)

        else:
            pass
    else:
        no_need_to_update()
