import json
from pathlib import Path
import numpy as np
from app.config import llm, EMBED_MODEL

POLICY_DIR = Path("data/policies")
CACHE = Path("data/policy_index.json")

def _embed(texts: list[str]) -> list[list[float]]:
    resp = llm.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def _build_index() -> list[dict]:
    chunks = []
    for f in sorted(POLICY_DIR.glob("*.txt")):
        for sentence in f.read_text(encoding="utf-8").split("."):
            sentence = sentence.strip()
            if sentence:
                chunks.append({"source": f.name, "text": sentence + "."})
    vectors = _embed([c["text"] for c in chunks])
    for c, v in zip(chunks, vectors):
        c["vector"] = v
    CACHE.write_text(json.dumps(chunks), encoding="utf-8")
    return chunks

def _load_index() -> list[dict]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return _build_index()

def search(query: str, top_k: int = 3) -> list[dict]:
    index = _load_index()
    q = np.array(_embed([query])[0])
    scored = []
    for c in index:
        v = np.array(c["vector"])
        score = float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v)))
        scored.append({"source": c["source"], "text": c["text"], "score": round(score, 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]