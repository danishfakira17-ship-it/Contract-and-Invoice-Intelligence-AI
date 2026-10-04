import asyncio, json
from app.agents import intake_agent, extraction_agent, compliance_agent

async def main():
    for f in ["inv_001_normal.pdf", "inv_002_high_value.pdf", "inv_004_autorenew.pdf"]:
        print("=" * 60, f)
        text = intake_agent.run(f"data/invoices/{f}")["text"]
        data = extraction_agent.run(text)["data"]
        out = await compliance_agent.run(data)
        print(json.dumps(out["result"], indent=2))

asyncio.run(main())