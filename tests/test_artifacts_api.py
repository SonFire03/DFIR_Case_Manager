from __future__ import annotations


def _create_case(client):
    res = client.post(
        "/api/cases",
        json={"title": "Artifacts test", "description": "", "severity": "medium", "priority": 3, "owner": "analyst"},
    )
    return res.json()["case_id"]


def test_artifact_crud(client):
    case_id = _create_case(client)

    add_res = client.post(
        f"/api/cases/{case_id}/artifacts",
        json={
            "artifact_type": "screenshot",
            "title": "Ransom note",
            "content": "/evidence/note.png",
            "description": "Desktop screenshot",
            "added_by": "analyst",
        },
    )
    assert add_res.status_code == 201
    artifact_id = add_res.json()["id"]

    list_res = client.get(f"/api/cases/{case_id}/artifacts")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    patch_res = client.patch(f"/api/artifacts/{artifact_id}", json={"title": "Updated title"})
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated title"

    delete_res = client.delete(f"/api/artifacts/{artifact_id}")
    assert delete_res.status_code == 204
