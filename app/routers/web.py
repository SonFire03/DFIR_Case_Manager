from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.services import (
    artifact_service,
    case_service,
    demo_service,
    ioc_service,
    note_service,
    report_service,
    timeline_service,
)

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)) -> Response:
    stats = case_service.dashboard_stats(db)
    recent_cases = case_service.list_cases(db)[:10]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"stats": stats, "cases": recent_cases},
    )


@router.get("/cases")
def cases_page(
    request: Request,
    status: models.CaseStatus | None = None,
    severity: models.CaseSeverity | None = None,
    owner: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
) -> Response:
    cases = case_service.list_cases(db, status=status, severity=severity, owner=owner, tag=tag)
    return templates.TemplateResponse(
        request=request,
        name="cases.html",
        context={
            "cases": cases,
            "status_values": [s.value for s in models.CaseStatus],
            "severity_values": [s.value for s in models.CaseSeverity],
            "filters": {
                "status": status.value if status else "",
                "severity": severity.value if severity else "",
                "owner": owner or "",
                "tag": tag or "",
            },
        },
    )


@router.post("/cases")
def create_case_web(
    title: str = Form(...),
    description: str = Form(""),
    severity: models.CaseSeverity = Form(models.CaseSeverity.MEDIUM),
    priority: int = Form(3),
    owner: str = Form(...),
    tags: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    case = case_service.create_case(
        db,
        schemas.CaseCreate(
            title=title,
            description=description,
            severity=severity,
            priority=priority,
            owner=owner,
            tags=tags,
        ),
    )
    return RedirectResponse(url=f"/cases/{case.case_id}", status_code=303)


@router.get("/cases/{case_id}")
def case_detail(request: Request, case_id: str, db: Session = Depends(get_db)) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        return RedirectResponse(url="/cases", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="case_detail.html",
        context={
            "case": case,
            "timeline": timeline_service.list_timeline_events(db, case),
            "iocs": ioc_service.list_case_iocs(db, case),
            "artifacts": artifact_service.list_artifacts(db, case),
            "notes": note_service.list_notes(db, case),
            "ioc_types": [i.value for i in models.IOCType],
            "confidence_levels": [c.value for c in models.ConfidenceLevel],
        },
    )


@router.post("/cases/{case_id}/close")
def close_case_web(case_id: str, db: Session = Depends(get_db)) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        case_service.close_case(db, case)
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/{case_id}/reopen")
def reopen_case_web(case_id: str, db: Session = Depends(get_db)) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        case_service.reopen_case(db, case)
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/{case_id}/timeline")
def add_timeline_web(
    case_id: str,
    title: str = Form(...),
    event_type: str = Form("generic"),
    details: str = Form(""),
    actor: str = Form("analyst"),
    db: Session = Depends(get_db),
) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        timeline_service.add_timeline_event(
            db,
            case,
            schemas.TimelineCreate(title=title, event_type=event_type, details=details, actor=actor),
        )
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/{case_id}/iocs")
def add_ioc_web(
    case_id: str,
    ioc_type: models.IOCType = Form(...),
    value: str = Form(...),
    source: str = Form(""),
    confidence: models.ConfidenceLevel = Form(models.ConfidenceLevel.MEDIUM),
    tags: str = Form(""),
    note: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        ioc_service.add_ioc(
            db,
            case,
            schemas.IOCCreate(
                ioc_type=ioc_type,
                value=value,
                source=source,
                confidence=confidence,
                tags=tags,
                note=note,
            ),
        )
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/{case_id}/artifacts")
def add_artifact_web(
    case_id: str,
    artifact_type: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    description: str = Form(""),
    added_by: str = Form("analyst"),
    db: Session = Depends(get_db),
) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        artifact_service.add_artifact(
            db,
            case,
            schemas.ArtifactCreate(
                artifact_type=artifact_type,
                title=title,
                content=content,
                description=description,
                added_by=added_by,
            ),
        )
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/{case_id}/notes")
def add_note_web(
    case_id: str,
    note: str = Form(...),
    author: str = Form("analyst"),
    important: bool = Form(False),
    db: Session = Depends(get_db),
) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if case:
        note_service.add_note(db, case, schemas.NoteCreate(note=note, author=author, important=important))
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.get("/cases/{case_id}/report")
def report_page(request: Request, case_id: str, db: Session = Depends(get_db)) -> Response:
    case = case_service.get_case_by_case_id(db, case_id)
    if not case:
        return RedirectResponse(url="/cases", status_code=303)
    report = report_service.case_to_report_payload(case)
    markdown_content = report_service.render_markdown(report)
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={"case": case, "report_md": markdown_content},
    )


@router.post("/demo/seed")
def seed_demo(force: bool = Form(False), db: Session = Depends(get_db)) -> Response:
    demo_service.seed_demo_data(db, force=force)
    return RedirectResponse(url="/", status_code=303)
