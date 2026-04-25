from __future__ import annotations


def _create_case(client, title="Ransomware alert", owner="bob", severity="high"):
    res = client.post(
        "/api/cases",
        json={
            "title": title,
            "description": "Host encrypted",
            "severity": severity,
            "priority": 1,
            "owner": owner,
            "tags": "ransomware,windows",
        },
    )
    assert res.status_code == 201
    return res.json()


def test_create_list_patch_close_reopen_case(client):
    created = _create_case(client)
    case_id = created["case_id"]

    list_res = client.get("/api/cases")
    assert list_res.status_code == 200
    assert any(c["case_id"] == case_id for c in list_res.json())

    patch_res = client.patch(f"/api/cases/{case_id}", json={"status": "in_progress", "owner": "charlie"})
    assert patch_res.status_code == 200
    assert patch_res.json()["owner"] == "charlie"

    close_res = client.post(f"/api/cases/{case_id}/close")
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "closed"

    reopen_res = client.post(f"/api/cases/{case_id}/reopen")
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "in_progress"


def test_case_filters(client):
    _create_case(client, title="Email phishing", owner="alice", severity="medium")
    _create_case(client, title="Critical malware", owner="alice", severity="critical")
    _create_case(client, title="Low noise", owner="bob", severity="low")

    by_owner = client.get("/api/cases", params={"owner": "alice"}).json()
    assert len(by_owner) == 2

    by_sev = client.get("/api/cases", params={"severity": "critical"}).json()
    assert len(by_sev) == 1
