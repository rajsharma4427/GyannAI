import pytest


def test_create_student_success(client):
    response = client.post("/api/students", json={"name": "Arjun", "lang": "en"})
    assert response.status_code == 201
    data = response.json()
    assert "student_id" in data
    assert data["student_id"].startswith("student_")

    # Verify student is persisted and graph can be retrieved
    graph_res = client.get(f"/api/graph/{data['student_id']}")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["states"]) > 0
    assert all(s["status"] == "unseen" for s in graph_data["states"])


def test_create_student_languages(client):
    for lang in ["en", "hi", "hinglish"]:
        res = client.post("/api/students", json={"name": f"Student_{lang}", "lang": lang})
        assert res.status_code == 201
        assert "student_id" in res.json()


def test_create_student_invalid_language(client):
    res = client.post("/api/students", json={"name": "Kavita", "lang": "french"})
    assert res.status_code in [400, 422]
    body = res.json()
    assert "error" in body
    assert "code" in body


def test_create_student_empty_name(client):
    res = client.post("/api/students", json={"name": "", "lang": "en"})
    assert res.status_code in [400, 422]
    body = res.json()
    assert "error" in body
    assert "code" in body
