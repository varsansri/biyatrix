import os
import tempfile
import json

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

from config import GROQ_API_KEY
from database import init_db, save_entry, get_recent_entries
from extract import extract
from embeddings import embed
from match import find_matches

app = FastAPI(title="biyatrix")
client = Groq(api_key=GROQ_API_KEY)

init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/dump")
async def dump_entry(
    text: str = Form(None),
    audio: UploadFile = File(None),
    user_id: str = Form("anonymous"),
):
    raw_text = text

    if audio:
        audio_bytes = await audio.read()
        suffix = ".webm"
        if audio.content_type and "mp4" in audio.content_type:
            suffix = ".mp4"
        elif audio.content_type and "ogg" in audio.content_type:
            suffix = ".ogg"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(tmp_path), f, audio.content_type or "audio/webm"),
                    model="whisper-large-v3",
                    response_format="text",
                )
            raw_text = str(transcription).strip()
        finally:
            os.unlink(tmp_path)

    if not raw_text or not raw_text.strip():
        raise HTTPException(status_code=400, detail="No content provided")

    extracted = extract(raw_text)
    embed_text = " ".join(filter(None, [
        extracted.get("problem"),
        extracted.get("summary"),
        raw_text[:300],
    ]))
    embedding = embed(embed_text)
    save_entry(user_id, raw_text, extracted, embedding)

    return {"status": "saved", "transcribed": raw_text, "extracted": extracted}


class FindRequest(BaseModel):
    query: str


@app.post("/find")
async def find(req: FindRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    matches = find_matches(req.query)
    return {"matches": matches}


@app.get("/feed")
async def feed():
    entries = get_recent_entries(30)
    result = []
    for e in entries:
        result.append({
            "id": e["id"],
            "summary": e.get("summary"),
            "problem": e.get("problem"),
            "domain": e.get("domain"),
            "emotion": e.get("emotion"),
            "stage": e.get("stage"),
            "tools": json.loads(e.get("tools") or "[]"),
            "created_at": e.get("created_at"),
        })
    return {"entries": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
