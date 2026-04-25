from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import case_service, note_service, timeline_service

router = APIRouter(prefix="/api", tags=["cases"])


def _get_case_or_404(db: Session, case_id: str) -> models.Case:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get("/cases", response_model=list[schemas.CaseRead])
def list_cases(
    status_filter: models.CaseStatus | None = Query(default=None, alias="status"),
    severity: models.CaseSeverity | None = None,
    owner: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
) -> list[models.Case]:
    return case_service.list_cases(db, status_filter, severity, owner, tag)


@router.post("/cases", response_model=schemas.CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)) -> models.Case:
    return case_service.create_case(db, payload)


@router.get("/cases/{case_id}", response_model=schemas.CaseRead)
def get_case(case_id: str, db: Session = Depends(get_db)) -> models.Case:
    return _get_case_or_404(db, case_id)


@router.patch("/cases/{case_id}", response_model=schemas.CaseRead)
def patch_case(case_id: str, payload: schemas.CaseUpdate, db: Session = Depends(get_db)) -> models.Case:
    case = _get_case_or_404(db, case_id)
    return case_service.update_case(db, case, payload)


@router.post("/cases/{case_id}/close", response_model=schemas.CaseRead)
def close_case(case_id: str, actor: str = "analyst", db: Session = Depends(get_db)) -> models.Case:
    case = _get_case_or_404(db, case_id)
    return case_service.close_case(db, case, actor=actor)


@router.post("/cases/{case_id}/reopen", response_model=schemas.CaseRead)
def reopen_case(case_id: str, actor: str = "analyst", db: Session = Depends(get_db)) -> models.Case:
    case = _get_case_or_404(db, case_id)
    return case_service.reopen_case(db, case, actor=actor)


@router.get("/cases/{case_id}/timeline", response_model=list[schemas.TimelineRead])
def list_timeline(case_id: str, db: Session = Depends(get_db)) -> list[models.TimelineEvent]:
    case = _get_case_or_404(db, case_id)
    return timeline_service.list_timeline_events(db, case)


@router.post("/cases/{case_id}/timeline", response_model=schemas.TimelineRead, status_code=status.HTTP_201_CREATED)
def add_timeline(case_id: str, payload: schemas.TimelineCreate, db: Session = Depends(get_db)) -> models.TimelineEvent:
    case = _get_case_or_404(db, case_id)
    return timeline_service.add_timeline_event(db, case, payload)


@router.get("/cases/{case_id}/notes", response_model=list[schemas.NoteRead])
def list_notes(case_id: str, db: Session = Depends(get_db)) -> list[models.AnalystNote]:
    case = _get_case_or_404(db, case_id)
    return note_service.list_notes(db, case)


@router.post("/cases/{case_id}/notes", response_model=schemas.NoteRead, status_code=status.HTTP_201_CREATED)
def add_note(case_id: str, payload: schemas.NoteCreate, db: Session = Depends(get_db)) -> models.AnalystNote:
    case = _get_case_or_404(db, case_id)
    return note_service.add_note(db, case, payload)
