import asyncio, os
from app.agents import orchestrator

# Start every test run from a clean state
for db in ["data/invoices.db", "data/app.db"]:
    if os.path.exists(db):
        os.remove(db)

async def main():
    for f in ["inv_001_normal.pdf", "inv_002_high_value.pdf", "inv_003_duplicate.pdf",
              "inv_004_autorenew.pdf", "inv_005_injection.pdf"]:
        r = await orchestrator.process(f"data/invoices/{f}", f)
        t = r["trace"]
        print(f"{f:28} -> {r['status']:17} | {t.get('decision_reason', t.get('error', ''))}")

asyncio.run(main())