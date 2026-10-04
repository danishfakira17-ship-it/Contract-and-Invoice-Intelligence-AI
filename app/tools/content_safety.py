import requests
from app.config import AI_ENDPOINT, AI_KEY

def shield_document(text: str) -> dict:
    """Ask Azure Prompt Shields whether the document contains an injection attack."""
    url = AI_ENDPOINT.rstrip("/") + "/contentsafety/text:shieldPrompt?api-version=2024-09-01"
    body = {"userPrompt": "Extract invoice data.", "documents": [text[:9000]]}
    headers = {"Ocp-Apim-Subscription-Key": AI_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        attack = r.json()["documentsAnalysis"][0]["attackDetected"]
        return {"available": True, "attack_detected": bool(attack)}
    except Exception as e:
        return {"available": False, "attack_detected": False, "error": str(e)[:200]}