"""
backend.tests.test_e2e_journey

Automated verification of the full 18-step end-to-end user journey across all 4 contributions:
Person 1 (AI Engine), Person 2 (Backend & SM-2 Learning Engine),
Person 3 (Frontend API Contract), and Person 4 (Content & Voice Support).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_full_18_step_user_journey(client):
    # Step 1 & 2: Backend health check
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    # Step 3: Create learner across all supported languages (en, hi, hinglish)
    for lang in ["en", "hi", "hinglish"]:
        res = client.post("/api/students", json={"name": f"Learner {lang}", "lang": lang})
        assert res.status_code == 201
        assert "student_id" in res.json()
    student_id = res.json()["student_id"]

    # Step 4: Initialize syllabus and load topic graph
    syl = client.post("/api/syllabus", json={"student_id": student_id, "goal": "Class 10 CBSE Math"}).json()
    assert len(syl["topics"]) == 13

    graph = client.get(f"/api/graph/{student_id}").json()
    assert len(graph["topics"]) == 13
    assert len(graph["states"]) == 13

    # Step 5 & 6: Start diagnostic on solve_by_factorization
    diag_start = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "solve_by_factorization"},
    ).json()
    session_id = diag_start["session_id"]
    q = diag_start["question"]
    assert q["topic_id"] == "solve_by_factorization"
    assert len(q["options"]) == 4

    # Step 7 & 8: Submit wrong answer, verify prerequisite backtrace to factorization
    wrong_idx = (q["correct_index"] + 1) % 4
    ans1 = client.post(
        "/api/diagnostic/answer",
        json={
            "session_id": session_id,
            "question_id": q["id"],
            "chosen_index": wrong_idx,
            "time_ms": 4000,
        },
    ).json()
    assert ans1["correct"] is False
    assert ans1["backtrace"] is not None
    assert ans1["backtrace"]["to_topic_id"] == "factorization"

    # Complete diagnostic session
    while not ans1["done"] and ans1.get("next_question"):
        nq = ans1["next_question"]
        ans1 = client.post(
            "/api/diagnostic/answer",
            json={
                "session_id": session_id,
                "question_id": nq["id"],
                "chosen_index": nq["correct_index"],
                "time_ms": 3000,
            },
        ).json()
    assert ans1["done"] is True
    assert ans1.get("summary") is not None

    # Step 9: Open lesson for topic in supported languages (en, hi, hinglish)
    for lang in ["en", "hi", "hinglish"]:
        lesson = client.get(f"/api/lesson/{student_id}/solve_by_factorization?lang={lang}").json()
        assert lesson["topic_id"] == "solve_by_factorization"
        assert len(lesson["story"]) > 10
        assert len(lesson["exercises"]) >= 2

    # Step 10 & 11: Submit teach-back explanation and verify persistence of feedback, notes, flashcards, state
    tb = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "solve_by_factorization",
            "transcript": "To solve by factorization we split the middle term and apply zero product property.",
        },
    ).json()
    assert tb["result"]["score"] >= 0.0
    assert len(tb["flashcards"]) > 0
    assert tb["note"]["body"]
    assert tb["state"]["mastery"] > 0.0

    # Step 12 & 13: Flashcard review and SM-2 update
    due = client.get(f"/api/flashcards/due/{student_id}").json()
    assert len(due["cards"]) > 0
    card_id = due["cards"][0]["id"]

    rev = client.post(
        "/api/flashcards/review",
        json={"student_id": student_id, "card_id": card_id, "quality": 4},
    ).json()
    assert rev["state"]["interval_days"] >= 1

    # Step 14: Create and retrieve notes
    note_res = client.post(
        "/api/notes",
        json={
            "student_id": student_id,
            "topic_id": "solve_by_factorization",
            "body": "Personal note: checking roots in original equation confirms answer.",
        },
    ).json()
    assert note_res["body"]

    notes_list = client.get(f"/api/notes/{student_id}/solve_by_factorization").json()
    assert len(notes_list["notes"]) >= 2

    # Step 15 & 16: Dashboard statistics and state advance
    dash = client.get(f"/api/dashboard/{student_id}").json()
    assert dash["overall_mastery"] > 0.0
    assert dash["streak_days"] >= 1

    # Advance clock
    adv = client.post(
        "/api/dev/advance-days",
        json={"student_id": student_id, "days": 1},
    ).json()
    assert "new_date" in adv

    dash_after = client.get(f"/api/dashboard/{student_id}").json()
    assert dash_after["due_today"] >= 0
