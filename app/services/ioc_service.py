from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.utils.formatters import normalize_tags


def list_case_iocs(db: Session, case: models.Case, query: str | None = None) -> list[models.CaseIOC]:
    stmt = select(models.CaseIOC).where(models.CaseIOC.case_id == case.id)
    if query:
        stmt = stmt.where(
            or_(
                models.CaseIOC.value.ilike(f"%{query}%"),
                models.CaseIOC.source.ilike(f"%{query}%"),
                models.CaseIOC.note.ilike(f"%{query}%"),
                models.CaseIOC.tags.ilike(f"%{query}%"),
            )
        )
    stmt = stmt.order_by(models.CaseIOC.created_at.desc())
    return list(db.scalars(stmt).all())


def add_ioc(db: Session, case: models.Case, payload: schemas.IOCCreate) -> models.CaseIOC:
    ioc = models.CaseIOC(
        case_id=case.id,
        ioc_type=payload.ioc_type,
        value=payload.value.strip(),
        source=payload.source,
        confidence=payload.confidence,
        tags=normalize_tags(payload.tags),
        note=payload.note,
    )
    db.add(ioc)
    db.flush()
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="ioc_added",
            title=f"IOC added: {ioc.ioc_type.value}",
            details=ioc.value,
            actor="analyst",
            linked_type="ioc",
            linked_id=str(ioc.id),
        )
    )
    db.commit()
    db.refresh(ioc)
    return ioc


def get_ioc(db: Session, ioc_id: int) -> models.CaseIOC | None:
    return db.get(models.CaseIOC, ioc_id)


def update_ioc(db: Session, ioc: models.CaseIOC, payload: schemas.IOCUpdate) -> models.CaseIOC:
    data = payload.model_dump(exclude_unset=True)
    if "tags" in data and data["tags"] is not None:
        data["tags"] = normalize_tags(data["tags"])
    for key, value in data.items():
        setattr(ioc, key, value)
    db.add(ioc)
    db.commit()
    db.refresh(ioc)
    return ioc


def delete_ioc(db: Session, ioc: models.CaseIOC) -> None:
    db.delete(ioc)
    db.commit()
