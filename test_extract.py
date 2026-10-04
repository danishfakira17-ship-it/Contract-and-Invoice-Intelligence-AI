import json
from app.agents import intake_agent, extraction_agent

for f in ["inv_001_normal.pdf", "inv_004_autorenew.pdf", "inv_005_injection.pdf"]:
    print("=" * 60, f)
    intake = intake_agent.run(f"data/invoices/{f}")
    print("Intake read", intake["chars"], "characters")
    result = extraction_agent.run(intake["text"])
    print(json.dumps(result["data"], indent=2))