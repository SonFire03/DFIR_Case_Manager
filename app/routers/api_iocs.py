from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import case_service, ioc_service

router = APIRouter(prefix="/api", tags=["iocs"])


@router.get("/cases/{case_id}/iocs", response_model=list[schemas.IOCRead])
def list_iocs(case_id: str, q: str | None = None, db: Session = Depends(get_db)) -> list[models.CaseIOC]:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return ioc_service.list_case_iocs(db, case, q)


@router.post("/cases/{case_id}/iocs", response_model=schemas.IOCRead, status_code=status.HTTP_201_CREATED)
def add_ioc(case_id: str, payload: schemas.IOCCreate, db: Session = Depends(get_db)) -> models.CaseIOC:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return ioc_service.add_ioc(db, case, payload)


@router.patch("/iocs/{ioc_id}", response_model=schemas.IOCRead)
def patch_ioc(ioc_id: int, payload: schemas.IOCUpdate, db: Session = Depends(get_db)) -> models.CaseIOC:
    ioc = ioc_service.get_ioc(db, ioc_id)
    if not ioc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IOC not found")
    return ioc_service.update_ioc(db, ioc, payload)


@router.delete("/iocs/{ioc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ioc(ioc_id: int, db: Session = Depends(get_db)) -> None:
    ioc = ioc_service.get_ioc(db, ioc_id)
    if not ioc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IOC not found")
    ioc_service.delete_ioc(db, ioc)
