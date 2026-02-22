import json
import os
import threading
import time
import unittest
from http.client import HTTPConnection

from app.db import DB_PATH, init_db
from app.server import Handler
from http.server import ThreadingHTTPServer


class TicketApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for suffix in ["", "-wal", "-shm"]:
            p = str(DB_PATH) + suffix
            if os.path.exists(p):
                os.remove(p)
        init_db()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def request(self, method, path, body=None):
        conn = HTTPConnection("127.0.0.1", self.port)
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(body) if body is not None else None
        conn.request(method, path, payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()
        return res.status, json.loads(data)

    def test_create_ticket_and_transition(self):
        status, data = self.request(
            "POST",
            "/api/tickets",
            {
                "customerName": "Alice",
                "mobileNumber": "9000000001",
                "address": "No 10",
                "googleMapLink": "https://maps.google.com/test",
                "complaintDescription": "No cooling",
                "priority": "High",
            },
        )
        self.assertEqual(status, 201)
        self.assertEqual(data["ticketNo"], "MXD-000001")
        self.assertEqual(data["status"], "New")

        bad_status, _ = self.request("PATCH", "/api/tickets/1/status", {"status": "Scheduled"})
        self.assertEqual(bad_status, 400)

        ok_status, data = self.request("PATCH", "/api/tickets/1/status", {"status": "Assigned"})
        self.assertEqual(ok_status, 200)
        self.assertEqual(data["status"], "Assigned")


if __name__ == "__main__":
    unittest.main()
