from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.config import AI_ENDPOINT, AI_KEY

_client = DocumentIntelligenceClient(AI_ENDPOINT, AzureKeyCredential(AI_KEY))

def read_pdf(path: str) -> str:
    """Send a PDF to Azure Document Intelligence and return its text."""
    with open(path, "rb") as f:
        data = f.read()
    poller = _client.begin_analyze_document(
        "prebuilt-read", body=data, content_type="application/octet-stream"
    )
    return poller.result().content