import pytest


def test_dashboard_metrics(client):
    res_st = client.post("/api/students", json={"name": "Dashboarder", "lang": "en"}).json()
    student_id = res_st["student_id"]

    # Initial state
    dash_res = client.get(f"/api/dashboard/{student_id}")
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert dash["overall_mastery"] == 0.0
    assert dash["topics_mastered"] == 0
    assert dash["topics_total"] > 0
    assert dash["due_today"] == 0
    assert dash["streak_days"] == 0
    assert len(dash["weakest"]) > 0

    # Submit a teachback to create mastery and flashcard
    client.post(
        "/api/teachback",
        json={
            "student_id": student_id,
            "topic_id": "quadratic_equations",
            "transcript": "Quadratic equations model parabolic trajectories.",
        },
    )

    dash_after = client.get(f"/api/dashboard/{student_id}").json()
    assert dash_after["overall_mastery"] > 0.0
    assert dash_after["due_today"] > 0
    assert dash_after["streak_days"] == 1


def test_dashboard_advancing_clock_and_streak(client):
    res_st = client.post("/api/students", json={"name": "Clock User", "lang": "en"}).json()
    student_id = res_st["student_id"]

    # Activity today
    client.post(
        "/api/notes",
        json={"student_id": student_id, "topic_id": "factorization", "body": "Day 1 note"},
    )
    assert client.get(f"/api/dashboard/{student_id}").json()["streak_days"] == 1

    # Advance clock by 1 day
    adv_res = client.post("/api/dev/advance-days", json={"student_id": student_id, "days": 1})
    assert adv_res.status_code == 200
    assert "new_date" in adv_res.json()

    # Activity on day 2
    client.post(
        "/api/notes",
        json={"student_id": student_id, "topic_id": "factorization", "body": "Day 2 note"},
    )
    assert client.get(f"/api/dashboard/{student_id}").json()["streak_days"] == 2
