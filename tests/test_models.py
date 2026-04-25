from __future__ import annotations

from app import models, schemas
from app.services import artifact_service, case_service, ioc_service, note_service, timeline_service


def test_model_relationships(db_session):
    case = case_service.create_case(
        db_session,
        schemas.CaseCreate(title="Suspicious outbound traffic", owner="alice", description="test"),
    )
    timeline_service.add_timeline_event(
        db_session,
        case,
        schemas.TimelineCreate(title="Triage started", event_type="triage_started", actor="alice"),
    )
    ioc_service.add_ioc(
        db_session,
        case,
        schemas.IOCCreate(ioc_type=models.IOCType.IP, value="10.10.10.10", source="edr"),
    )
    artifact_service.add_artifact(
        db_session,
        case,
        schemas.ArtifactCreate(artifact_type="log_path", title="EDR log", content="/tmp/edr.log"),
    )
    note_service.add_note(db_session, case, schemas.NoteCreate(note="Initial triage done", author="alice"))

    loaded = case_service.get_case_by_case_id(db_session, case.case_id)
    assert loaded is not None
    assert len(loaded.timeline_events) >= 2  # includes case_created
    assert len(loaded.iocs) == 1
    assert len(loaded.artifacts) == 1
    assert len(loaded.notes) == 1
