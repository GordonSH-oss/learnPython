"""Minimal FastAPI app for backend learning.

Run:
    cd 12-web-backend
    uvicorn fastapi_app:app --reload
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - educational dependency hint
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/web.txt") from exc


class NoteCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=80)]
    body: Annotated[str, Field(min_length=1)]


class NoteOut(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime


@dataclass
class Note:
    id: str
    title: str
    body: str
    created_at: datetime


app = FastAPI(title="Python Learning Notes API")
notes: dict[str, Note] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(payload: NoteCreate) -> Note:
    note = Note(
        id=str(uuid4()),
        title=payload.title,
        body=payload.body,
        created_at=datetime.now(timezone.utc),
    )
    notes[note.id] = note
    return note


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: str) -> Note:
    try:
        return notes[note_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"error": "note_not_found", "note_id": note_id}) from exc
