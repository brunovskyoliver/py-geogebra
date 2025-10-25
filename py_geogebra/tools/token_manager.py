import json
import os
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.token_file = os.path.expanduser('~/.py_geogebra/auth.json')
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)

    def save_token(self, access_token: str, user_info: dict) -> None:
        data = {
            'access_token': access_token,
            'user_info': user_info,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.token_file, 'w') as f:
            json.dump(data, f)

    def load_token(self):
        try:
            if not os.path.exists(self.token_file):
                return None

            with open(self.token_file, 'r') as f:
                data = json.load(f)

            saved_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - saved_time > timedelta(hours=23):
                return None

            return {
                'access_token': data['access_token'],
                'user_info': data['user_info']
            }
        except Exception as e:
            return None

    def clear_token(self) -> None:
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
