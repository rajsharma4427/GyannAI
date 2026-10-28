import pytest


def test_diagnostic_starts_at_difficulty_2(client):
    res_st = client.post("/api/students", json={"name": "Diag Student", "lang": "en"})
    student_id = res_st.json()["student_id"]

    res = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "quadratic_equations"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "question" in data
    assert data["question"]["difficulty"] == 2
    assert data["question"]["topic_id"] == "quadratic_equations"
    assert len(data["question"]["options"]) == 4


def test_correct_answer_increases_difficulty(client):
    res_st = client.post("/api/students", json={"name": "Ace Student", "lang": "en"})
    student_id = res_st.json()["student_id"]

    start = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "quadratic_equations"},
    ).json()

    session_id = start["session_id"]
    q = start["question"]

    # Submit correct answer (q["correct_index"])
    ans_res = client.post(
        "/api/diagnostic/answer",
        json={
            "session_id": session_id,
            "question_id": q["id"],
            "chosen_index": q["correct_index"],
            "time_ms": 1200,
        },
    )
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["correct"] is True
    if not ans_data["done"]:
        assert ans_data["next_question"]["difficulty"] == min(3, q["difficulty"] + 1)


def test_wrong_answer_decreases_difficulty(client):
    res_st = client.post("/api/students", json={"name": "Struggling Student", "lang": "en"})
    student_id = res_st.json()["student_id"]

    start = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "quadratic_equations"},
    ).json()

    session_id = start["session_id"]
    q = start["question"]

    # Submit intentionally wrong answer
    wrong_index = (q["correct_index"] + 1) % 4
    ans_res = client.post(
        "/api/diagnostic/answer",
        json={
            "session_id": session_id,
            "question_id": q["id"],
            "chosen_index": wrong_index,
            "time_ms": 2000,
        },
    )
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["correct"] is False
    if not ans_data["done"]:
        assert ans_data["next_question"]["difficulty"] == max(1, q["difficulty"] - 1)


def test_cannot_answer_completed_session(client):
    res_st = client.post("/api/students", json={"name": "Quick Student", "lang": "en"})
    student_id = res_st.json()["student_id"]

    start = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "quadratic_equations"},
    ).json()
    session_id = start["session_id"]
    curr_q = start["question"]

    # Answer questions until session completes (at most 8)
    for _ in range(8):
        ans = client.post(
            "/api/diagnostic/answer",
            json={
                "session_id": session_id,
                "question_id": curr_q["id"],
                "chosen_index": (curr_q["correct_index"] + 1) % 4,
                "time_ms": 1000,
            },
        ).json()
        if ans["done"]:
            break
        curr_q = ans["next_question"]

    # Now attempt to answer again
    replay = client.post(
        "/api/diagnostic/answer",
        json={
            "session_id": session_id,
            "question_id": curr_q["id"],
            "chosen_index": 0,
            "time_ms": 1000,
        },
    )
    assert replay.status_code == 400
    assert replay.json()["code"] == "SESSION_ALREADY_COMPLETED"
