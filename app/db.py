import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "app.db"
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(schema)


def ticket_no(ticket_id: int) -> str:
    return f"MXD-{ticket_id:06d}"


def upsert_customer(conn, name, mobile_number, address, google_map_link):
    row = conn.execute(
        "SELECT id FROM customers WHERE mobile_number = ?", (mobile_number,)
    ).fetchone()
    if row:
        conn.execute(
            """
            UPDATE customers
            SET name = ?, address = ?, google_map_link = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (name, address, google_map_link, row["id"]),
        )
        return row["id"]

    cur = conn.execute(
        """
        INSERT INTO customers (name, mobile_number, address, google_map_link)
        VALUES (?, ?, ?, ?)
        """,
        (name, mobile_number, address, google_map_link),
    )
    return cur.lastrowid
