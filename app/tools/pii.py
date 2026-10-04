from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from app.config import AI_ENDPOINT, AI_KEY

_client = TextAnalyticsClient(AI_ENDPOINT, AzureKeyCredential(AI_KEY))

def mask_pii(text: str) -> dict:
    """Find personal data and return masked text."""
    try:
        res = _client.recognize_pii_entities([text[:5000]], language="en")[0]
        if res.is_error:
            return {"available": False, "masked_text": text, "found": []}
        found = [{"type": e.category, "text": e.text} for e in res.entities]
        return {"available": True, "masked_text": res.redacted_text, "found": found}
    except Exception as e:
        return {"available": False, "masked_text": text, "found": [], "error": str(e)[:200]}