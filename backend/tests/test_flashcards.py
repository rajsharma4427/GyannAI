import pytest


def test_flashcards_isolation_and_due_queue(client):
    res_a = client.post("/api/students", json={"name": "Alice", "lang": "en"}).json()
    res_b = client.post("/api/students", json={"name": "Bob", "lang": "en"}).json()
    student_a = res_a["student_id"]
    student_b = res_b["student_id"]

    # Alice does a teach-back which generates flashcards
    tb_res = client.post(
        "/api/teachback",
        json={
            "student_id": student_a,
            "topic_id": "quadratic_equations",
            "transcript": "Quadratic equations are of degree two.",
        },
    ).json()

    # Alice should have due cards
    due_a = client.get(f"/api/flashcards/due/{student_a}").json()
    assert len(due_a["cards"]) > 0

    # Bob should have ZERO cards (isolation!)
    due_b = client.get(f"/api/flashcards/due/{student_b}").json()
    assert len(due_b["cards"]) == 0


def test_flashcard_review_quality_validation(client):
    res_st = client.post("/api/students", json={"name": "Reviewer", "lang": "en"}).json()
    student_id = res_st["student_id"]

    tb_res = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": "Roots are solutions to equations.",
        },
    ).json()
    card_id = tb_res["flashcards"][0]["id"]

    # Reject quality > 5
    res_high = client.post(
        "/api/flashcards/review",
        json={"student_id": student_id, "card_id": card_id, "quality": 6},
    )
    assert res_high.status_code == 400
    assert res_high.json()["code"] == "INVALID_QUALITY"

    # Reject quality < 0
    res_low = client.post(
        "/api/flashcards/review",
        json={"student_id": student_id, "card_id": card_id, "quality": -1},
    )
    assert res_low.status_code == 400
    assert res_low.json()["code"] == "INVALID_QUALITY"


def test_flashcard_review_updates_srs_state(client):
    res_st = client.post("/api/students", json={"name": "SRS User", "lang": "en"}).json()
    student_id = res_st["student_id"]

    tb_res = client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": "Standard form is ax^2 + bx + c = 0.",
        },
    ).json()
    card_id = tb_res["flashcards"][0]["id"]

    # Successful review with quality 4
    rev_res = client.post(
        "/api/flashcards/review",
        json={"student_id": student_id, "card_id": card_id, "quality": 4},
    )
    assert rev_res.status_code == 200
    updated_state = rev_res.json()["state"]
    assert updated_state["interval_days"] == 1
    assert updated_state["next_review"] is not None

    # Card is now scheduled for tomorrow, so no longer due today!
    due_cards = client.get(f"/api/flashcards/due/{student_id}").json()["cards"]
    assert not any(c["id"] == card_id for c in due_cards)
