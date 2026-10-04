import asyncio
from app import database
from app.tools import invoice_db
from app.agents import (intake_agent, guardrail_agent, extraction_agent,
                        compliance_agent, risk_agent, communication_agent)

async def process(pdf_path: str, filename: str, doc_id: int | None = None) -> dict:
    if doc_id is None:
        doc_id = database.create(filename)
    trace = {}

    try:
        # 1. Intake (sync Azure call, run in a thread so the server isn't blocked)
        intake = await asyncio.to_thread(intake_agent.run, pdf_path)
        trace["intake"] = {"chars": intake["chars"]}

        # 2. Guardrail: stop immediately on attack
        guard = await asyncio.to_thread(guardrail_agent.run, intake["text"])
        trace["guardrail"] = {k: v for k, v in guard.items() if k != "masked_text"}
        if guard["verdict"] == "block":
            trace["decision_reason"] = "Prompt injection detected: blocked before processing"
            database.save_result(doc_id, "blocked", 100, "high", None, None, trace)
            return {"id": doc_id, "status": "blocked", "trace": trace}

        # 3. Extraction
        extracted = await asyncio.to_thread(extraction_agent.run, intake["text"])
        data = extracted["data"]
        trace["extraction"] = data

        # 4. Compliance and Risk in parallel
        compliance, risk = await asyncio.gather(
            compliance_agent.run(data),
            risk_agent.run(data),
        )
        trace["compliance"] = compliance["result"]
        trace["compliance_rules_used"] = compliance["rules_used"]
        trace["risk"] = {k: v for k, v in risk.items() if k != "agent"}

        # 5. Decision
        duplicate = any("DUPLICATE" in s for s in risk["signals"])
        compliant = compliance["result"].get("status") == "compliant"
        approvals = compliance["result"].get("required_approvals", [])

        if duplicate:
            status = "rejected"
            trace["decision_reason"] = "Duplicate invoice rejected automatically"
        elif (risk["level"] == "low" and compliant and not approvals
              and (data.get("total") or 0) <= 10000):
            status = "approved"
            trace["decision_reason"] = "Low risk and compliant: auto-approved"
        else:
            status = "pending_approval"
            trace["decision_reason"] = "Needs human review"
            mail = await communication_agent.run(data, compliance["result"], risk)
            trace["email"] = mail["email"]

        # 6. Remember this invoice so a second copy is caught as a duplicate
        if status != "rejected" and data.get("invoice_number") and data.get("vendor"):
            invoice_db.register(data["invoice_number"], data["vendor"])

        database.save_result(doc_id, status, risk["score"], risk["level"],
                             data.get("vendor"), data.get("total"), trace)
        return {"id": doc_id, "status": status, "trace": trace}

    except Exception as e:
        trace["error"] = str(e)[:300]
        database.save_result(doc_id, "error", 0, "unknown", None, None, trace)
        return {"id": doc_id, "status": "error", "trace": trace}