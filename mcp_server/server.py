import sys
from mcp.server.fastmcp import FastMCP
from app.tools import invoice_db, policy_search

mcp = FastMCP("invoice-tools")

@mcp.tool()
def check_duplicate_invoice(invoice_number: str, vendor: str) -> dict:
    """Check whether this invoice number from this vendor was already processed."""
    return {"duplicate": invoice_db.is_duplicate(invoice_number, vendor)}

@mcp.tool()
def lookup_vendor(vendor: str) -> dict:
    """Look up a vendor in the company vendor list (mock ERP)."""
    return invoice_db.vendor_info(vendor)

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email (mock: logs it instead of sending)."""
    print(f"[MOCK EMAIL] to={to} subject={subject}", file=sys.stderr, flush=True)
    return {"sent": True, "to": to, "subject": subject}

@mcp.tool()
def search_policies(query: str, top_k: int = 3) -> dict:
    """Search company policies and return the most relevant rules."""
    return {"results": policy_search.search(query, top_k)}


if __name__ == "__main__":
    mcp.run()