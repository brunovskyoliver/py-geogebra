import gettext
import os
import sys


def set_language(lang: str):
    if getattr(
        sys, "frozen", False
    ):  # https://pyinstaller.org/en/stable/runtime-information.html
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    localedir = os.path.join(base_path, "locales")

    translation = gettext.translation(
        domain="messages", localedir=localedir, languages=[lang], fallback=True
    )
    translation.install()
    return translation.gettext
