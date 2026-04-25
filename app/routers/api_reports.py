from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import case_service, report_service

router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/cases/{case_id}/report.md", response_class=PlainTextResponse)
def report_markdown(case_id: str, db: Session = Depends(get_db)) -> str:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    payload = report_service.case_to_report_payload(case)
    return report_service.render_markdown(payload)


@router.get("/cases/{case_id}/report.html", response_class=HTMLResponse)
def report_html(case_id: str, db: Session = Depends(get_db)) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    payload = report_service.case_to_report_payload(case)
    markdown_content = report_service.render_markdown(payload)
    safe_html = "<br>".join(markdown_content.splitlines())
    return HTMLResponse(f"<html><body><pre>{safe_html}</pre></body></html>")


@router.get("/cases/{case_id}/report.json", response_class=JSONResponse)
def report_json(case_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return report_service.case_to_report_payload(case)
