import pytest


def test_create_and_list_notes(client):
    res_st = client.post("/api/students", json={"name": "Notes Student", "lang": "en"}).json()
    student_id = res_st["student_id"]

    # Create note
    res_note = client.post(
        "/api/notes",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "body": "Remember: middle term splitting requires ac = product and b = sum.",
        },
    )
    assert res_note.status_code == 201
    note_data = res_note.json()
    assert note_data["author"] == "student"
    assert "middle term splitting" in note_data["body"]
    assert "created_at" in note_data

    # List notes
    list_res = client.get(f"/api/notes/{student_id}/quadratic_equations")
    assert list_res.status_code == 200
    notes = list_res.json()["notes"]
    assert len(notes) >= 1
    assert any(n["id"] == note_data["id"] for n in notes)


def test_notes_student_isolation(client):
    res_a = client.post("/api/students", json={"name": "Student A", "lang": "en"}).json()
    res_b = client.post("/api/students", json={"name": "Student B", "lang": "en"}).json()
    s_a = res_a["student_id"]
    s_b = res_b["student_id"]

    client.post(
        "/api/notes",
        json={"student_id": s_a, "topic_id": "factorization", "body": "Secret note of A"},
    )

    notes_b = client.get(f"/api/notes/{s_b}/factorization").json()["notes"]
    assert len(notes_b) == 0


def test_create_note_empty_body(client):
    res_st = client.post("/api/students", json={"name": "User", "lang": "en"}).json()
    student_id = res_st["student_id"]

    res = client.post(
        "/api/notes",
        json={"student_id": student_id, "topic_id": "factorization", "body": "   "},
    )
    assert res.status_code == 400
    assert res.json()["code"] == "EMPTY_BODY"
