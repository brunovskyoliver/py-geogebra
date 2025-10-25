import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import threading
from .auth_config import AUTH0_DOMAIN, AUTH0_CALLBACK_URL, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, API_AUDIENCE
from .token_manager import TokenManager

class Auth0Handler:
    def __init__(self):
        self.access_token = None
        self.callback = threading.Event()
        self.auth_code = None
        self.token_manager = TokenManager()
        token = self.token_manager.load_token()
        if token:
            self.access_token = token['access_token']
            self.user_info = token['user_info']
        else:
            self.user_info = None

    def create_callback_handler(self):
        class Callback(http.server.SimpleHTTPRequestHandler):
            def do_GET(handler):
                raw = urllib.parse.urlparse(handler.path)
                d = urllib.parse.parse_qs(raw.query)
                if 'code' in d:
                    self.auth_code = d['code'][0]
                    self.callback.set()
                handler.send_response(200)
                handler.send_header('Content-type', 'text/html')
                handler.end_headers()
                handler.wfile.write(b"""
                    <html>
                    <head><title>Auth0</title></head>
                    <body>
                        <h1>Hotovo</h1>
                    </body>
                    </html>
                """.strip())

        return Callback

    def authenticate(self):
        with socketserver.TCPServer(("localhost", 3000), self.create_callback_handler()) as httpd:
            params = {
                'response_type': 'code',
                'client_id': AUTH0_CLIENT_ID,
                'redirect_uri': AUTH0_CALLBACK_URL,
                'scope': 'openid profile email',
                'audience': API_AUDIENCE
            }
            auth_url = f"https://{AUTH0_DOMAIN}/authorize?" + urllib.parse.urlencode(params)
            webbrowser.open(auth_url)
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            callback = self.callback.wait(timeout=300)
            if not self.auth_code:
                return None
            token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
            token_payload = {
                'grant_type': 'authorization_code',
                'client_id': AUTH0_CLIENT_ID,
                'client_secret': AUTH0_CLIENT_SECRET,
                'code': self.auth_code,
                'redirect_uri': AUTH0_CALLBACK_URL
            }

            try:
                token = requests.post(token_url, json=token_payload)
                if token.status_code == 200:
                    token_data = token.json()
                    self.access_token = token_data['access_token']
                    return self.access_token
                else:
                    return None
            except Exception as e:
                return None

    def get_user_info(self):
        if self.user_info:
            return self.user_info
        if not self.access_token:
            return None
        headers = {'Authorization': f'Bearer {self.access_token}'}
        user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
        try:
            response = requests.get(user_info_url, headers=headers)
            if response.status_code == 200:
                self.user_info = response.json()
                self.token_manager.save_token(self.access_token, self.user_info)
                return self.user_info
        except Exception as e:
            return None

        return None
