from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def list_timeline_events(db: Session, case: models.Case) -> list[models.TimelineEvent]:
    stmt = (
        select(models.TimelineEvent)
        .where(models.TimelineEvent.case_id == case.id)
        .order_by(models.TimelineEvent.timestamp.asc())
    )
    return list(db.scalars(stmt).all())


def add_timeline_event(db: Session, case: models.Case, payload: schemas.TimelineCreate) -> models.TimelineEvent:
    event = models.TimelineEvent(
        case_id=case.id,
        timestamp=payload.timestamp,
        event_type=payload.event_type,
        title=payload.title,
        details=payload.details,
        actor=payload.actor,
        linked_type=payload.linked_type,
        linked_id=payload.linked_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
