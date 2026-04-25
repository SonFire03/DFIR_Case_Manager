from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import artifact_service, case_service

router = APIRouter(prefix="/api", tags=["artifacts"])


@router.get("/cases/{case_id}/artifacts", response_model=list[schemas.ArtifactRead])
def list_artifacts(case_id: str, db: Session = Depends(get_db)) -> list[models.Artifact]:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return artifact_service.list_artifacts(db, case)


@router.post("/cases/{case_id}/artifacts", response_model=schemas.ArtifactRead, status_code=status.HTTP_201_CREATED)
def add_artifact(case_id: str, payload: schemas.ArtifactCreate, db: Session = Depends(get_db)) -> models.Artifact:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return artifact_service.add_artifact(db, case, payload)


@router.patch("/artifacts/{artifact_id}", response_model=schemas.ArtifactRead)
def patch_artifact(artifact_id: int, payload: schemas.ArtifactUpdate, db: Session = Depends(get_db)) -> models.Artifact:
    artifact = artifact_service.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    return artifact_service.update_artifact(db, artifact, payload)


@router.delete("/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(artifact_id: int, db: Session = Depends(get_db)) -> None:
    artifact = artifact_service.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    artifact_service.delete_artifact(db, artifact)
