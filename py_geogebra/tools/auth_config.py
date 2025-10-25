import os
from dotenv import load_dotenv
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    env_path = os.path.join(sys._MEIPASS, '.env')
else:
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


load_dotenv(env_path)
TURSO_URL = os.getenv("TURSO_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
API_AUDIENCE = os.getenv("API_AUDIENCE")
