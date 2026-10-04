# Contract & Invoice Intelligence: Multi-Agent System on Azure AI

AI agents that read vendor invoices, check them against company policy, flag
risk, and route risky ones to a human for approval.

## Architecture

Upload (HTML/JS) -> FastAPI -> Orchestrator -> agents -> SQLite -> Dashboard

| Agent | Job | Azure service |
|---|---|---|
| Guardrail | Prompt-injection and PII checks | Content Safety (Prompt Shields), Language |
| Intake | Read PDF | Document Intelligence |
| Extraction | Text to validated JSON | Azure OpenAI gpt-4.1-mini + Pydantic |
| Compliance | Policy check with RAG and citations | text-embedding-3-small + gpt-4.1-mini |
| Risk | Duplicates, unknown vendors, amounts | MCP tools + gpt-4.1-mini |
| Communication | Drafts approval email | gpt-4.1-mini + MCP tool |

A custom **MCP server** exposes the enterprise tools (policy search, duplicate
check, vendor lookup, email). Agents call them as MCP clients.
Compliance and Risk run in parallel. Anything above $10,000 or with risk
signals goes to human approval.

## Run locally

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# create .env with your Azure keys (see .env.example)
python make_sample_data.py
uvicorn app.main:app --reload
```

## Evaluation (5-document benchmark)

- Decision accuracy: 15/15 = 95%
- Extraction accuracy: 8/8 = 100%
- Average time per document: 19.2 s

## Design decisions

- AI judges; deterministic code enforces hard limits and computes risk scores.
- Layered guardrails: Azure Prompt Shields plus keyword backup.
- Untrusted document text is treated as data, never as instructions.
- Full agent trace and audit trail stored for every document.

## Limitations

Mock ERP and email; 3 sample policies; PDF only; small benchmark.