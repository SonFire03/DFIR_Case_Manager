from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.utils.formatters import normalize_tags, utc_now
from app.utils.validators import ensure_non_empty


def _next_case_id(db: Session) -> str:
    count = db.scalar(select(func.count(models.Case.id))) or 0
    return f"CASE-{utc_now().year}-{count + 1:04d}"


def get_case_by_case_id(db: Session, case_id: str) -> models.Case | None:
    return db.scalar(select(models.Case).where(models.Case.case_id == case_id))


def list_cases(
    db: Session,
    status: models.CaseStatus | None = None,
    severity: models.CaseSeverity | None = None,
    owner: str | None = None,
    tag: str | None = None,
) -> list[models.Case]:
    stmt = select(models.Case)
    if status:
        stmt = stmt.where(models.Case.status == status)
    if severity:
        stmt = stmt.where(models.Case.severity == severity)
    if owner:
        stmt = stmt.where(models.Case.owner.ilike(f"%{owner}%"))
    if tag:
        stmt = stmt.where(models.Case.tags.ilike(f"%{tag.lower()}%"))
    stmt = stmt.order_by(models.Case.updated_at.desc())
    return list(db.scalars(stmt).all())


def create_case(db: Session, payload: schemas.CaseCreate) -> models.Case:
    title = ensure_non_empty(payload.title, "title")
    owner = ensure_non_empty(payload.owner, "owner")
    case = models.Case(
        case_id=payload.case_id or _next_case_id(db),
        title=title,
        description=payload.description,
        status=models.CaseStatus.OPEN,
        severity=payload.severity,
        priority=payload.priority,
        owner=owner,
        tags=normalize_tags(payload.tags),
    )
    db.add(case)
    db.flush()
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="case_created",
            title="Case created",
            details=f"Case {case.case_id} created",
            actor=owner,
        )
    )
    db.commit()
    db.refresh(case)
    return case


def update_case(db: Session, case: models.Case, payload: schemas.CaseUpdate) -> models.Case:
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"]:
        data["title"] = ensure_non_empty(data["title"], "title")
    if "owner" in data and data["owner"]:
        data["owner"] = ensure_non_empty(data["owner"], "owner")
    if "tags" in data and data["tags"] is not None:
        data["tags"] = normalize_tags(data["tags"])

    for key, value in data.items():
        setattr(case, key, value)

    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def close_case(db: Session, case: models.Case, actor: str = "analyst") -> models.Case:
    case.status = models.CaseStatus.CLOSED
    case.closed_at = utc_now()
    db.add(case)
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="case_closed",
            title="Case closed",
            details="Case marked as closed",
            actor=actor,
        )
    )
    db.commit()
    db.refresh(case)
    return case


def reopen_case(db: Session, case: models.Case, actor: str = "analyst") -> models.Case:
    case.status = models.CaseStatus.IN_PROGRESS
    case.closed_at = None
    db.add(case)
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="case_reopened",
            title="Case reopened",
            details="Case reopened for further investigation",
            actor=actor,
        )
    )
    db.commit()
    db.refresh(case)
    return case


def dashboard_stats(db: Session) -> dict[str, int]:
    open_cases = (
        db.scalar(select(func.count(models.Case.id)).where(models.Case.status != models.CaseStatus.CLOSED)) or 0
    )
    high_severity = (
        db.scalar(
            select(func.count(models.Case.id)).where(
                models.Case.severity.in_([models.CaseSeverity.CRITICAL, models.CaseSeverity.HIGH])
            )
        )
        or 0
    )
    recently_updated = (
        db.scalar(select(func.count(models.Case.id)).where(models.Case.updated_at >= func.datetime("now", "-2 days")))
        or 0
    )
    closed_week = (
        db.scalar(
            select(func.count(models.Case.id)).where(
                models.Case.closed_at.is_not(None), models.Case.closed_at >= func.datetime("now", "-7 days")
            )
        )
        or 0
    )
    return {
        "open_cases": open_cases,
        "high_severity_cases": high_severity,
        "recently_updated": recently_updated,
        "closed_this_week": closed_week,
    }
