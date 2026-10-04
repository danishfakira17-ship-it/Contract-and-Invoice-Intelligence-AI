import sqlite3

DB = "data/invoices.db"

KNOWN_VENDORS = {
    "Acme Supplies Pvt Ltd": {"status": "approved", "country": "IN"},
    "Globex Industrial": {"status": "approved", "country": "US"},
    "CloudNova Software": {"status": "approved", "country": "US"},
}

def _conn():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS seen (invoice_number TEXT, vendor TEXT)")
    return c

def is_duplicate(invoice_number: str, vendor: str) -> bool:
    with _conn() as c:
        row = c.execute(
            "SELECT 1 FROM seen WHERE invoice_number=? AND vendor=?",
            (invoice_number, vendor),
        ).fetchone()
    return row is not None

def register(invoice_number: str, vendor: str) -> None:
    with _conn() as c:
        c.execute("INSERT INTO seen VALUES (?, ?)", (invoice_number, vendor))

def vendor_info(vendor: str) -> dict:
    return KNOWN_VENDORS.get(vendor, {"status": "unknown", "country": None})