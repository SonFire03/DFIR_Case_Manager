from __future__ import annotations


def test_report_endpoints(client):
    create = client.post(
        "/api/cases",
        json={
            "title": "Report test",
            "description": "investigation",
            "severity": "high",
            "priority": 2,
            "owner": "dfir",
        },
    )
    case_id = create.json()["case_id"]

    client.post(
        f"/api/cases/{case_id}/iocs",
        json={"ioc_type": "ip", "value": "8.8.8.8", "source": "log", "confidence": "low"},
    )
    client.post(
        f"/api/cases/{case_id}/notes",
        json={"note": "Escalate to IR lead", "author": "dfir", "important": True},
    )

    md = client.get(f"/api/cases/{case_id}/report.md")
    assert md.status_code == 200
    assert "Incident Report" in md.text

    html = client.get(f"/api/cases/{case_id}/report.html")
    assert html.status_code == 200
    assert "<html>" in html.text

    js = client.get(f"/api/cases/{case_id}/report.json")
    assert js.status_code == 200
    assert js.json()["case_id"] == case_id
