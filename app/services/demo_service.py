from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.services import artifact_service, case_service, ioc_service, note_service, timeline_service


def seed_demo_data(db: Session, force: bool = False) -> int:
    existing = db.scalar(select(func.count(models.Case.id))) or 0
    if existing > 0 and not force:
        return 0

    if force and existing > 0:
        for case in list(db.scalars(select(models.Case)).all()):
            db.delete(case)
        db.commit()

    case_1 = case_service.create_case(
        db,
        schemas.CaseCreate(
            case_id="CASE-2026-1001",
            title="Phishing-driven credential theft on finance workstation",
            description=("Suspicious OAuth consent and impossible travel alert detected after phishing email click."),
            severity=models.CaseSeverity.HIGH,
            priority=1,
            owner="soc_analyst",
            tags="phishing,identity,o365",
        ),
    )

    timeline_service.add_timeline_event(
        db,
        case_1,
        schemas.TimelineCreate(
            event_type="alert_received",
            title="Alert received from IdP",
            details="Impossible travel + MFA fatigue indicators.",
            actor="soc_analyst",
        ),
    )
    timeline_service.add_timeline_event(
        db,
        case_1,
        schemas.TimelineCreate(
            event_type="triage_started",
            title="Triage started",
            details="Correlated email gateway, IdP and endpoint logs.",
            actor="ir_lead",
        ),
    )
    ioc_service.add_ioc(
        db,
        case_1,
        schemas.IOCCreate(
            ioc_type=models.IOCType.DOMAIN,
            value="login-m365-security-check.example",
            source="email_gateway",
            confidence=models.ConfidenceLevel.HIGH,
            tags="phishing,credential_harvest",
            note="Domain used in lure URL.",
        ),
    )
    ioc_service.add_ioc(
        db,
        case_1,
        schemas.IOCCreate(
            ioc_type=models.IOCType.IP,
            value="185.203.116.77",
            source="proxy_logs",
            confidence=models.ConfidenceLevel.MEDIUM,
            tags="c2,suspicious",
            note="Observed after credential submission.",
        ),
    )
    artifact_service.add_artifact(
        db,
        case_1,
        schemas.ArtifactCreate(
            artifact_type="command_output",
            title="IdP audit query",
            content="SigninLogs | where UserPrincipalName == 'finance.user@corp.local'",
            description="Cloud identity investigation query output reference.",
            added_by="soc_analyst",
        ),
    )
    note_service.add_note(
        db,
        case_1,
        schemas.NoteCreate(
            note="Password reset completed. Token revocation forced for impacted account.",
            author="ir_lead",
            important=True,
        ),
    )

    case_2 = case_service.create_case(
        db,
        schemas.CaseCreate(
            case_id="CASE-2026-1002",
            title="Suspected ransomware staging on file server",
            description="EDR flagged rapid file enumeration and shadow copy deletion attempt.",
            severity=models.CaseSeverity.CRITICAL,
            priority=1,
            owner="dfir_oncall",
            tags="ransomware,windows,server",
        ),
    )

    timeline_service.add_timeline_event(
        db,
        case_2,
        schemas.TimelineCreate(
            event_type="host_isolated",
            title="Host isolated",
            details="Server isolated at switch and EDR containment enabled.",
            actor="soc_analyst",
        ),
    )
    ioc_service.add_ioc(
        db,
        case_2,
        schemas.IOCCreate(
            ioc_type=models.IOCType.HASH,
            value="b1946ac92492d2347c6235b4d2611184f66a4f7d7d0f7a7a4f5f9a3ab0ec8d41",
            source="edr",
            confidence=models.ConfidenceLevel.HIGH,
            tags="payload,ransomware",
            note="Suspicious executable hash from quarantined binary.",
        ),
    )
    artifact_service.add_artifact(
        db,
        case_2,
        schemas.ArtifactCreate(
            artifact_type="log_path",
            title="Sysmon Event Log Extract",
            content="C:/IR/evidence/server42/sysmon_2026-04-25.evtx",
            description="Collected during initial containment.",
            added_by="dfir_oncall",
        ),
    )
    note_service.add_note(
        db,
        case_2,
        schemas.NoteCreate(
            note="No encryption observed yet. Lateral movement indicators under review.",
            author="dfir_oncall",
            important=True,
        ),
    )

    return 2
