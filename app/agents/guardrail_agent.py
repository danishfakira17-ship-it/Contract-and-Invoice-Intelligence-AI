from app.tools.content_safety import shield_document
from app.tools.pii import mask_pii

KEYWORDS = ["ignore all previous", "ignore previous instructions",
            "disregard", "approve this invoice", "risk score 0"]

def run(text: str) -> dict:
    shield = shield_document(text)
    pii = mask_pii(text)

    lowered = text.lower()
    keyword_hit = any(k in lowered for k in KEYWORDS)

    attack = shield["attack_detected"] or keyword_hit
    return {
        "agent": "guardrail",
        "attack_detected": attack,
        "shield_available": shield["available"],
        "detected_by": ("prompt_shields" if shield["attack_detected"]
                        else "keywords" if keyword_hit else None),
        "pii_found": pii["found"],
        "masked_text": pii["masked_text"],
        "verdict": "block" if attack else "allow",
    }