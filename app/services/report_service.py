from __future__ import annotations

from typing import Any

from app import models


def case_to_report_payload(case: models.Case) -> dict[str, Any]:
    timeline = [
        {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "title": event.title,
            "details": event.details,
            "actor": event.actor,
        }
        for event in sorted(case.timeline_events, key=lambda x: x.timestamp)
    ]
    iocs = [
        {
            "ioc_type": ioc.ioc_type.value,
            "value": ioc.value,
            "source": ioc.source,
            "confidence": ioc.confidence.value,
            "tags": ioc.tags,
            "note": ioc.note,
        }
        for ioc in case.iocs
    ]
    artifacts = [
        {
            "artifact_type": artifact.artifact_type,
            "title": artifact.title,
            "content": artifact.content,
            "description": artifact.description,
            "added_by": artifact.added_by,
        }
        for artifact in case.artifacts
    ]
    important_notes = [
        {"author": n.author, "note": n.note, "created_at": n.created_at.isoformat()} for n in case.notes if n.important
    ]

    return {
        "case_id": case.case_id,
        "title": case.title,
        "description": case.description,
        "status": case.status.value,
        "severity": case.severity.value,
        "priority": case.priority,
        "owner": case.owner,
        "tags": case.tags,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "timeline": timeline,
        "iocs": iocs,
        "artifacts": artifacts,
        "important_notes": important_notes,
        "actions_remediation": [
            "Contain affected hosts and isolate compromised assets.",
            "Block malicious IOCs at network and email gateways.",
            "Perform credential hygiene and monitor for re-compromise.",
        ],
        "conclusion": "Investigation completed with collected evidence, linked IOCs, and analyst notes.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Incident Report - {report['case_id']}")
    lines.append("")
    lines.append("## Case Summary")
    lines.append(f"- Title: {report['title']}")
    lines.append(f"- Status: {report['status']}")
    lines.append(f"- Severity: {report['severity']}")
    lines.append(f"- Owner: {report['owner']}")
    lines.append(f"- Description: {report['description']}")
    lines.append("")

    lines.append("## Timeline")
    for ev in report["timeline"]:
        lines.append(f"- {ev['timestamp']} | {ev['event_type']} | {ev['title']} ({ev['actor']})")
    lines.append("")

    lines.append("## IOC")
    for ioc in report["iocs"]:
        lines.append(f"- {ioc['ioc_type']}: {ioc['value']} ({ioc['confidence']})")
    lines.append("")

    lines.append("## Artifacts")
    for artifact in report["artifacts"]:
        lines.append(f"- {artifact['artifact_type']} | {artifact['title']} | {artifact['description']}")
    lines.append("")

    lines.append("## Important Notes")
    for note in report["important_notes"]:
        lines.append(f"- [{note['author']}] {note['note']}")
    lines.append("")

    lines.append("## Actions / Remediation")
    for action in report["actions_remediation"]:
        lines.append(f"- {action}")
    lines.append("")

    lines.append("## Conclusion")
    lines.append(str(report["conclusion"]))

    return "\n".join(lines)
