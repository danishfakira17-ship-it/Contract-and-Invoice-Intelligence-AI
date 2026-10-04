import sqlite3, json
from datetime import datetime

DB = "data/app.db"

def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        status TEXT,
        risk_score INTEGER,
        risk_level TEXT,
        vendor TEXT,
        total REAL,
        trace TEXT,
        created_at TEXT,
        decided_by TEXT,
        decided_at TEXT
    )""")
    return c

def create(filename: str) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO documents (filename, status, created_at) VALUES (?, 'processing', ?)",
            (filename, datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid

def save_result(doc_id: int, status: str, risk_score: int, risk_level: str,
                vendor: str, total: float, trace: dict) -> None:
    with _conn() as c:
        c.execute(
            """UPDATE documents SET status=?, risk_score=?, risk_level=?,
               vendor=?, total=?, trace=? WHERE id=?""",
            (status, risk_score, risk_level, vendor, total, json.dumps(trace), doc_id),
        )

def get(doc_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["trace"] = json.loads(d["trace"]) if d["trace"] else {}
    return d

def list_all() -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            """SELECT id, filename, status, risk_score, risk_level, vendor, total, created_at
               FROM documents ORDER BY id DESC"""
        ).fetchall()
    return [dict(r) for r in rows]

def decide(doc_id: int, approved: bool, who: str = "reviewer") -> None:
    status = "approved" if approved else "rejected"
    with _conn() as c:
        c.execute(
            "UPDATE documents SET status=?, decided_by=?, decided_at=? WHERE id=?",
            (status, who, datetime.now().isoformat(timespec="seconds"), doc_id),
        )