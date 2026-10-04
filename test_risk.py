import asyncio, json
from app.agents import intake_agent, extraction_agent, compliance_agent, risk_agent, communication_agent
from app.tools import invoice_db

async def main():
    # Pretend INV-1001 was processed earlier so inv_003 is a true duplicate
    invoice_db.register("INV-1001", "Acme Supplies Pvt Ltd")

    for f in ["inv_001_normal.pdf", "inv_002_high_value.pdf", "inv_003_duplicate.pdf",
              "inv_004_autorenew.pdf", "inv_005_injection.pdf"]:
        print("=" * 60, f)
        text = intake_agent.run(f"data/invoices/{f}")["text"]
        data = extraction_agent.run(text)["data"]
        risk = await risk_agent.run(data)
        print("RISK:", risk["score"], risk["level"])
        print("SIGNALS:", risk["signals"])
        print("WHY:", risk["explanation"])

    # Test the Communication Agent once, on the last invoice
    comp = (await compliance_agent.run(data))["result"]
    mail = await communication_agent.run(data, comp, risk)
    print("=" * 60, "EMAIL")
    print(mail["email"]["subject"])
    print(mail["email"]["body"])

asyncio.run(main())