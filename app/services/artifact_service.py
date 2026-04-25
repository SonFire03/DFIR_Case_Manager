from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def list_artifacts(db: Session, case: models.Case) -> list[models.Artifact]:
    stmt = select(models.Artifact).where(models.Artifact.case_id == case.id).order_by(models.Artifact.created_at.desc())
    return list(db.scalars(stmt).all())


def add_artifact(db: Session, case: models.Case, payload: schemas.ArtifactCreate) -> models.Artifact:
    artifact = models.Artifact(
        case_id=case.id,
        artifact_type=payload.artifact_type,
        title=payload.title,
        content=payload.content,
        description=payload.description,
        added_by=payload.added_by,
    )
    db.add(artifact)
    db.flush()
    db.add(
        models.TimelineEvent(
            case_id=case.id,
            event_type="artifact_added",
            title=f"Artifact added: {artifact.title}",
            details=artifact.artifact_type,
            actor=payload.added_by,
            linked_type="artifact",
            linked_id=str(artifact.id),
        )
    )
    db.commit()
    db.refresh(artifact)
    return artifact


def get_artifact(db: Session, artifact_id: int) -> models.Artifact | None:
    return db.get(models.Artifact, artifact_id)


def update_artifact(db: Session, artifact: models.Artifact, payload: schemas.ArtifactUpdate) -> models.Artifact:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(artifact, key, value)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def delete_artifact(db: Session, artifact: models.Artifact) -> None:
    db.delete(artifact)
    db.commit()
