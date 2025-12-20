import os
import subprocess
import sys
import requests

APP_DIR = os.path.join(os.environ["LOCALAPPDATA"], "PyGeogebra")
API_URL = "https://api.github.com/repos/brunovskyoliver/py-geogebra/releases/latest"


def get_version():
    versions = sorted(d for d in os.listdir(APP_DIR) if d.startswith("v"))
    return versions[-1] if versions else None

def run(version):
    path = os.path.join(APP_DIR, version)
    for f in os.listdir(path):
        if f.endswith(".exe"):
            subprocess.Popen([os.path.join(path, f)], close_fds=True)
            sys.exit(0)

def install():
    r = requests.get(API_URL, timeout=5)
    r.raise_for_status()
    for a in r.json()["assets"]:
        if a["name"].endswith("-windows.exe"):
            exe_url = a["browser_download_url"]
            break
    else:
        sys.exit("Nenasla sa instalacka")

    tmp = os.path.join(APP_DIR, "download.exe")
    with requests.get(exe_url, stream=True) as dl, open(tmp, "wb") as f:
        f.write(dl.content)

    version = r.json()["tag_name"]
    target = os.path.join(APP_DIR, version)
    os.makedirs(target, exist_ok=True)
    final_exe = os.path.join(target, "py-geogebra.exe")
    os.replace(tmp, final_exe)
    run(version)

def main():
    os.makedirs(APP_DIR, exist_ok=True)
    v = get_version()
    if v:
        run(v)
    else:
        install()

if __name__ == "__main__":
    main()

