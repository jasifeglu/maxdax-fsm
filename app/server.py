import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app.db import get_conn, init_db, ticket_no, upsert_customer
from app.status import WORKFLOW, can_transition, next_status

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
PRIORITIES = ["Low", "Medium", "High", "Urgent"]


def ticket_from_row(row):
    return {
        "id": row["id"],
        "ticketNo": row["ticket_no"],
        "complaintDescription": row["complaint_description"],
        "priority": row["priority"],
        "status": row["status"],
        "nextStatus": next_status(row["status"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "customer": {
            "id": row["customer_id"],
            "name": row["customer_name"],
            "mobileNumber": row["mobile_number"],
            "address": row["address"],
            "googleMapLink": row["google_map_link"],
        },
    }


class Handler(BaseHTTPRequestHandler):
    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(body.decode("utf-8"))

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self):
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"
        file_path = (PUBLIC_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(PUBLIC_DIR)) or not file_path.exists():
            self.send_error(404)
            return
        data = file_path.read_bytes()
        content_type = "text/html" if file_path.suffix == ".html" else "text/plain"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/status-workflow":
            return self._send_json(200, {"workflow": WORKFLOW})
        if path == "/api/tickets":
            with get_conn() as conn:
                rows = conn.execute(
                    """
                    SELECT t.*, c.id AS customer_id, c.name AS customer_name, c.mobile_number, c.address, c.google_map_link
                    FROM tickets t JOIN customers c ON c.id = t.customer_id
                    ORDER BY t.id DESC
                    """
                ).fetchall()
            return self._send_json(200, [ticket_from_row(r) for r in rows])

        m = re.match(r"^/api/tickets/(\d+)$", path)
        if m:
            ticket_id = int(m.group(1))
            with get_conn() as conn:
                row = conn.execute(
                    """
                    SELECT t.*, c.id AS customer_id, c.name AS customer_name, c.mobile_number, c.address, c.google_map_link
                    FROM tickets t JOIN customers c ON c.id = t.customer_id WHERE t.id = ?
                    """,
                    (ticket_id,),
                ).fetchone()
                if not row:
                    return self._send_json(404, {"error": "Ticket not found"})
                history = conn.execute(
                    """
                    SELECT from_status AS fromStatus, to_status AS toStatus, note, changed_at AS changedAt
                    FROM ticket_status_history WHERE ticket_id = ? ORDER BY id
                    """,
                    (ticket_id,),
                ).fetchall()
            payload = ticket_from_row(row)
            payload["history"] = [dict(h) for h in history]
            return self._send_json(200, payload)

        return self._serve_static()

    def do_POST(self):
        if urlparse(self.path).path != "/api/tickets":
            return self._send_json(404, {"error": "Not found"})
        data = self._read_json()
        required = ["customerName", "mobileNumber", "complaintDescription", "priority"]
        if any(not data.get(k) for k in required):
            return self._send_json(400, {"error": "Missing required fields"})
        if data["priority"] not in PRIORITIES:
            return self._send_json(400, {"error": "Invalid priority"})

        status = data.get("status", "New")
        if status not in WORKFLOW:
            return self._send_json(400, {"error": "Invalid status"})

        with get_conn() as conn:
            customer_id = upsert_customer(
                conn,
                data["customerName"],
                data["mobileNumber"],
                data.get("address"),
                data.get("googleMapLink"),
            )
            cur = conn.execute(
                """
                INSERT INTO tickets (customer_id, complaint_description, priority, status)
                VALUES (?, ?, ?, ?)
                """,
                (customer_id, data["complaintDescription"], data["priority"], status),
            )
            ticket_id = cur.lastrowid
            conn.execute(
                "UPDATE tickets SET ticket_no = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (ticket_no(ticket_id), ticket_id),
            )
            conn.execute(
                """
                INSERT INTO ticket_status_history (ticket_id, from_status, to_status, note)
                VALUES (?, NULL, ?, 'Ticket created')
                """,
                (ticket_id, status),
            )
            conn.commit()
            row = conn.execute(
                """
                SELECT t.*, c.id AS customer_id, c.name AS customer_name, c.mobile_number, c.address, c.google_map_link
                FROM tickets t JOIN customers c ON c.id = t.customer_id WHERE t.id = ?
                """,
                (ticket_id,),
            ).fetchone()
        return self._send_json(201, ticket_from_row(row))

    def do_PATCH(self):
        m = re.match(r"^/api/tickets/(\d+)/status$", urlparse(self.path).path)
        if not m:
            return self._send_json(404, {"error": "Not found"})
        ticket_id = int(m.group(1))
        data = self._read_json()
        new_status = data.get("status")
        if not new_status:
            return self._send_json(400, {"error": "status is required"})

        with get_conn() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            if not row:
                return self._send_json(404, {"error": "Ticket not found"})
            if not can_transition(row["status"], new_status):
                return self._send_json(400, {"error": "Invalid status transition"})
            conn.execute(
                "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_status, ticket_id),
            )
            conn.execute(
                """
                INSERT INTO ticket_status_history (ticket_id, from_status, to_status, note)
                VALUES (?, ?, ?, ?)
                """,
                (ticket_id, row["status"], new_status, data.get("note")),
            )
            conn.commit()
            res = conn.execute(
                """
                SELECT t.*, c.id AS customer_id, c.name AS customer_name, c.mobile_number, c.address, c.google_map_link
                FROM tickets t JOIN customers c ON c.id = t.customer_id WHERE t.id = ?
                """,
                (ticket_id,),
            ).fetchone()
        return self._send_json(200, ticket_from_row(res))


def run(port=3000):
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
