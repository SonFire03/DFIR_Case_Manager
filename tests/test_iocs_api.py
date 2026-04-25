from __future__ import annotations


def _create_case(client):
    res = client.post(
        "/api/cases",
        json={"title": "IOC test", "description": "", "severity": "high", "priority": 2, "owner": "analyst"},
    )
    return res.json()["case_id"]


def test_ioc_crud_and_search(client):
    case_id = _create_case(client)

    add_res = client.post(
        f"/api/cases/{case_id}/iocs",
        json={
            "ioc_type": "domain",
            "value": "evil.example",
            "source": "threat_feed",
            "confidence": "high",
            "tags": "phishing",
            "note": "Seen in campaign",
        },
    )
    assert add_res.status_code == 201
    ioc_id = add_res.json()["id"]

    list_res = client.get(f"/api/cases/{case_id}/iocs")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    search_res = client.get(f"/api/cases/{case_id}/iocs", params={"q": "evil"})
    assert len(search_res.json()) == 1

    patch_res = client.patch(f"/api/iocs/{ioc_id}", json={"confidence": "medium"})
    assert patch_res.status_code == 200
    assert patch_res.json()["confidence"] == "medium"

    delete_res = client.delete(f"/api/iocs/{ioc_id}")
    assert delete_res.status_code == 204
