from __future__ import annotations


def _create_case(client):
    res = client.post(
        "/api/cases",
        json={"title": "Timeline test", "description": "", "severity": "medium", "priority": 3, "owner": "analyst"},
    )
    return res.json()["case_id"]


def test_timeline_list_and_create(client):
    case_id = _create_case(client)

    create_res = client.post(
        f"/api/cases/{case_id}/timeline",
        json={"event_type": "alert_received", "title": "Alert received", "details": "EDR alert", "actor": "soc"},
    )
    assert create_res.status_code == 201

    list_res = client.get(f"/api/cases/{case_id}/timeline")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 2  # includes case_created event
