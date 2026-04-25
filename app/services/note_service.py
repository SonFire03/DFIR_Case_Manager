from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def list_notes(db: Session, case: models.Case) -> list[models.AnalystNote]:
    stmt = (
        select(models.AnalystNote)
        .where(models.AnalystNote.case_id == case.id)
        .order_by(models.AnalystNote.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def add_note(db: Session, case: models.Case, payload: schemas.NoteCreate) -> models.AnalystNote:
    note = models.AnalystNote(case_id=case.id, note=payload.note, author=payload.author, important=payload.important)
    db.add(note)
    db.flush()
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="note_added",
            title="Analyst note added",
            details=(payload.note[:120] + "...") if len(payload.note) > 120 else payload.note,
            actor=payload.author,
            linked_type="note",
            linked_id=str(note.id),
        )
    )
    db.commit()
    db.refresh(note)
    return note
