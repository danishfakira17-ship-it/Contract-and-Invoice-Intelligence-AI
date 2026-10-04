import asyncio, os, time
from app.agents import orchestrator

# Start clean
for db in ["data/invoices.db", "data/app.db"]:
    if os.path.exists(db):
        os.remove(db)

CASES = [
    # file, expected status, expected invoice no, expected total
    ("inv_001_normal.pdf",     "approved",         "INV-1001", 4700.0),
    ("inv_002_high_value.pdf", "pending_approval", "INV-1002", 50500.0),
    ("inv_003_duplicate.pdf",  "rejected",         "INV-1001", 4700.0),
    ("inv_004_autorenew.pdf",  "pending_approval", "INV-1004", 12000.0),
    ("inv_005_injection.pdf",  "blocked",          None,       None),
]

async def main():
    decision_ok = field_ok = field_total = 0
    times = []
    print(f"{'file':26}{'expected':18}{'got':18}{'sec':>6}")
    for f, exp_status, exp_no, exp_total in CASES:
        t0 = time.time()
        r = await orchestrator.process(f"data/invoices/{f}", f)
        sec = time.time() - t0
        times.append(sec)
        ok = r["status"] == exp_status
        decision_ok += ok
        print(f"{f:26}{exp_status:18}{r['status']:18}{sec:6.1f} {'OK' if ok else 'MISMATCH'}")

        ext = r["trace"].get("extraction")
        if ext and exp_no:
            field_total += 2
            field_ok += (ext.get("invoice_number") == exp_no)
            field_ok += (ext.get("total") == exp_total)

    n = len(CASES)
    print("\n--- RESULTS (put these on your resume) ---")
    print(f"Decision accuracy : {decision_ok}/{n} = {100*decision_ok/n:.0f}%")
    print(f"Extraction accuracy: {field_ok}/{field_total} = {100*field_ok/field_total:.0f}%")
    print(f"Avg time/document : {sum(times)/n:.1f} s")

asyncio.run(main())