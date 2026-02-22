import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

from src.auth_system import bootstrap_default_store, require_roles

store, auth = bootstrap_default_store()


def parse_json(handler: BaseHTTPRequestHandler) -> Dict:
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length) if length else b"{}"
    return json.loads(body.decode("utf-8"))


class RequestHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, data: Dict):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _auth_payload(self):
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise PermissionError("Missing Bearer token")
        token = auth_header.split(" ", 1)[1]
        return auth.verify_jwt(token)

    def do_POST(self):
        try:
            if self.path == "/auth/login":
                data = parse_json(self)
                self._send(200, auth.login(data["username"], data["password"]))
                return

            if self.path == "/admin/technicians":
                payload = self._auth_payload()
                require_roles(payload, ["Admin"])
                data = parse_json(self)
                created = auth.create_technician(payload["role"], data["username"])
                self._send(201, created)
                return

            if self.path == "/auth/password-reset/request":
                data = parse_json(self)
                token = auth.request_password_reset(data["username"])
                self._send(200, {"reset_token": token})
                return

            if self.path == "/auth/password-reset/confirm":
                data = parse_json(self)
                auth.confirm_password_reset(data["token"], data["new_password"])
                self._send(200, {"message": "Password updated"})
                return

            self._send(404, {"error": "Not found"})
        except PermissionError as err:
            self._send(403, {"error": str(err)})
        except ValueError as err:
            self._send(400, {"error": str(err)})
        except KeyError:
            self._send(400, {"error": "Missing required field"})

    def do_GET(self):
        try:
            if self.path == "/me":
                payload = self._auth_payload()
                self._send(200, {"username": payload["sub"], "role": payload["role"]})
                return
            self._send(404, {"error": "Not found"})
        except PermissionError as err:
            self._send(403, {"error": str(err)})
        except ValueError as err:
            self._send(401, {"error": str(err)})


def run(host: str = "0.0.0.0", port: int = 8000):
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
