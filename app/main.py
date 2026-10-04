import shutil
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import database
from app.agents import orchestrator

app = FastAPI(title="Contract & Invoice Intelligence")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR = Path("frontend")


async def _process_in_background(path: str, filename: str, doc_id: int):
    await orchestrator.process(path, filename, doc_id)


@app.post("/upload")
async def upload(background: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    saved = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"
    with open(saved, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc_id = database.create(file.filename)
    background.add_task(_process_in_background, str(saved), file.filename, doc_id)
    return {"id": doc_id, "status": "processing"}


@app.get("/documents")
def list_documents():
    return database.list_all()


@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    doc = database.get(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


def _decide(doc_id: int, approved: bool):
    doc = database.get(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc["status"] != "pending_approval":
        raise HTTPException(400, f"Cannot decide: status is '{doc['status']}'")
    database.decide(doc_id, approved)
    return database.get(doc_id)


@app.post("/documents/{doc_id}/approve")
def approve(doc_id: int):
    return _decide(doc_id, True)


@app.post("/documents/{doc_id}/reject")
def reject(doc_id: int):
    return _decide(doc_id, False)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")