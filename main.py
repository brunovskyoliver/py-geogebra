import os, sys

lib_path = os.path.join(os.path.dirname(__file__), "lib")
plat = sys.platform
if plat == "darwin":
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = lib_path
from py_geogebra.app import run_app

if __name__ == "__main__":
    run_app()
