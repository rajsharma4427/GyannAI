import pytest


def test_full_end_to_end_flow(client):
    """Full End-to-End Test for Person 2 Backend & Learning Engine:
    Create student → assign seeded syllabus → load graph → start diagnostic →
    answer incorrectly → observe backtrace → finish diagnostic → fetch lesson →
    submit teach-back → generate and store flashcards/note → review a card →
    advance demo days → confirm the due queue and dashboard update.
    """
    # 1. Create student
    st_res = client.post("/api/students", json={"name": "Pooja Sharma", "lang": "en"})
    assert st_res.status_code == 201
    student_id = st_res.json()["student_id"]

    # 2. Assign seeded syllabus
    syl_res = client.post(
        "/api/syllabus",
        json={"student_id": student_id, "goal": "Class 10 CBSE Board Exam Prep"},
    )
    assert syl_res.status_code == 200
    topics = syl_res.json()["topics"]
    assert len(topics) >= 13

    # 3. Load graph
    graph_res = client.get(f"/api/graph/{student_id}")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["topics"]) == len(topics)
    assert len(graph_data["states"]) == len(topics)

    # 4. Start diagnostic on quadratic_equations
    diag_start = client.post(
        "/api/diagnostic/start",
        json={"student_id": student_id, "topic_id": "quadratic_equations"},
    )
    assert diag_start.status_code == 200
    start_data = diag_start.json()
    session_id = start_data["session_id"]
    current_q = start_data["question"]
    assert current_q["topic_id"] == "quadratic_equations"
    assert current_q["difficulty"] == 2

    # 5. Answer incorrectly -> Observe backtrace to prerequisite
    wrong_choice = (current_q["correct_index"] + 1) % 4
    ans_1 = client.post(
        "/api/diagnostic/answer",
        json={
            "session_id": session_id,
            "question_id": current_q["id"],
            "chosen_index": wrong_choice,
            "time_ms": 1500,
        },
    )
    assert ans_1.status_code == 200
    data_1 = ans_1.json()
    assert data_1["correct"] is False

    # Backtrace should be triggered pointing towards a prerequisite (e.g. factorization)
    assert data_1["backtrace"] is not None
    assert data_1["backtrace"]["from_topic_id"] == "quadratic_equations"
    assert data_1["backtrace"]["to_topic_id"] in ["factorization", "polynomials", "linear_equations"]
    assert len(data_1["backtrace"]["reason"]) > 0

    # 6. Continue diagnostic until completion
    curr_q = data_1["next_question"]
    summary = None
    for _ in range(8):
        if curr_q is None:
            break
        # Answer correctly on prerequisite to confirm root or finish
        resp = client.post(
            "/api/diagnostic/answer",
            json={
                "session_id": session_id,
                "question_id": curr_q["id"],
                "chosen_index": curr_q["correct_index"],
                "time_ms": 1000,
            },
        ).json()
        if resp["done"]:
            summary = resp["summary"]
            break
        curr_q = resp["next_question"]

    # Verify diagnostic finished and summary is present
    assert summary is not None or resp["done"] is True

    # 7. Fetch lesson
    lesson_res = client.get(f"/api/lesson/{student_id}/quadratic_equations?lang=en")
    assert lesson_res.status_code == 200
    lesson = lesson_res.json()
    assert lesson["topic_id"] == "quadratic_equations"
    assert len(lesson["story"]) > 0
    assert len(lesson["explanation"]) > 0
    assert len(lesson["key_terms"]) > 0
    assert len(lesson["exercises"]) >= 2

    # 8. Submit teach-back
    tb_res = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": (
                "A quadratic equation is written in the form ax^2 + bx + c = 0. "
                "The roots can be found by splitting the middle term to factorize into two linear expressions, "
                "or by computing the discriminant b^2 - 4ac and using the quadratic formula."
            ),
        },
    )
    assert tb_res.status_code == 200
    tb_data = tb_res.json()
    assert tb_data["result"]["score"] > 0
    assert len(tb_data["flashcards"]) > 0
    assert tb_data["note"]["author"] == "ai"
    assert tb_data["state"]["mastery"] > 0
    card_to_review = tb_data["flashcards"][0]

    # 9. Verify notes exist
    notes_res = client.get(f"/api/notes/{student_id}/quadratic_equations")
    assert notes_res.status_code == 200
    notes_list = notes_res.json()["notes"]
    assert any(n["author"] == "ai" for n in notes_list)

    # Add a student note
    add_note = client.post(
        "/api/notes",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "body": "My personal takeaway: always check if a is zero before applying formula.",
        },
    )
    assert add_note.status_code == 201

    # 10. Check due flashcards
    due_res = client.get(f"/api/flashcards/due/{student_id}")
    assert due_res.status_code == 200
    due_cards = due_res.json()["cards"]
    assert any(c["id"] == card_to_review["id"] for c in due_cards)

    # 11. Review flashcard with quality 4 (SM-2 schedules it 1 day in the future)
    review_res = client.post(
        "/api/flashcards/review",
        json={
            "student_id": student_id,
            "card_id": card_to_review["id"],
            "quality": 4,
        },
    )
    assert review_res.status_code == 200
    assert review_res.json()["state"]["interval_days"] == 1

    # Card should no longer be due today
    due_now = client.get(f"/api/flashcards/due/{student_id}").json()["cards"]
    assert not any(c["id"] == card_to_review["id"] for c in due_now)

    # 12. Advance demo clock by 1 day
    adv_res = client.post(
        "/api/dev/advance-days",
        json={"student_id": student_id, "days": 1},
    )
    assert adv_res.status_code == 200

    # 13. Card is now due again!
    due_after_advance = client.get(f"/api/flashcards/due/{student_id}").json()["cards"]
    assert any(c["id"] == card_to_review["id"] for c in due_after_advance)

    # 14. Check dashboard
    dash_res = client.get(f"/api/dashboard/{student_id}")
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert dash["overall_mastery"] > 0
    assert dash["due_today"] >= 1
    assert dash["streak_days"] >= 1
    assert len(dash["weakest"]) > 0
