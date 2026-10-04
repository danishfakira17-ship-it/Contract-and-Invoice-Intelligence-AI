import json
from app.agents import intake_agent, guardrail_agent

for f in ["inv_001_normal.pdf", "inv_005_injection.pdf"]:
    print("=" * 60, f)
    text = intake_agent.run(f"data/invoices/{f}")["text"]
    g = guardrail_agent.run(text)
    print(json.dumps({k: v for k, v in g.items() if k != "masked_text"}, indent=2))