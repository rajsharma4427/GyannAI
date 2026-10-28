import pytest


def test_submit_teachback_success(client):
    res_st = client.post("/api/students", json={"name": "Teachback User", "lang": "en"})
    student_id = res_st.json()["student_id"]

    res = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": (
                "A quadratic equation has the standard form ax^2 + bx + c = 0 where a cannot be zero. "
                "We can solve it by factoring the quadratic trinomial into linear terms or using the quadratic formula."
            ),
        },
    )
    assert res.status_code == 200
    data = res.json()

    assert "result" in data
    assert data["result"]["score"] >= 0.0
    assert "covered" in data["result"]
    assert "feedback" in data["result"]

    assert "flashcards" in data
    assert len(data["flashcards"]) > 0
    assert all(c["source"] == "teachback" for c in data["flashcards"])

    assert "note" in data
    assert data["note"]["author"] == "ai"
    assert data["note"]["topic_id"] == "quadratic_equations"

    assert "state" in data
    assert data["state"]["mastery"] > 0.0


def test_submit_teachback_empty_transcript(client):
    res_st = client.post("/api/students", json={"name": "Empty User", "lang": "en"})
    student_id = res_st.json()["student_id"]

    res = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": "   ",
        },
    )
    assert res.status_code == 400
    assert res.json()["code"] == "EMPTY_TRANSCRIPT"


def test_submit_teachback_nonexistent_student(client):
    res = client.post(
        "/api/teachback",
        json={
            "student_id": "fake_student",
            "topic_id": "quadratic_equations",
            "transcript": "Valid transcript text here.",
        },
    )
    assert res.status_code == 404
    assert res.json()["code"] == "STUDENT_NOT_FOUND"
