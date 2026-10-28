import pytest
from backend.contracts import Topic
from backend.engine.backtrace import validate_topic_graph, GraphValidationError
from backend.db import get_db


def test_syllabus_from_text(client):
    res_st = client.post("/api/students", json={"name": "Test User", "lang": "en"})
    student_id = res_st.json()["student_id"]

    res = client.post(
        "/api/syllabus",
        json={"student_id": student_id, "text": "Class 10 Quadratic Equations and Polynomials"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "topics" in data
    assert len(data["topics"]) > 0


def test_syllabus_from_goal(client):
    res_st = client.post("/api/students", json={"name": "Goal User", "lang": "en"})
    student_id = res_st.json()["student_id"]

    res = client.post(
        "/api/syllabus",
        json={"student_id": student_id, "goal": "Master Quadratic Equations for Boards"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "topics" in data
    assert len(data["topics"]) > 0


def test_syllabus_requires_exactly_one_of_text_or_goal(client):
    res_st = client.post("/api/students", json={"name": "Goal User", "lang": "en"})
    student_id = res_st.json()["student_id"]

    # Both provided
    res_both = client.post(
        "/api/syllabus",
        json={"student_id": student_id, "text": "some text", "goal": "some goal"},
    )
    assert res_both.status_code == 400

    # Neither provided
    res_none = client.post(
        "/api/syllabus",
        json={"student_id": student_id},
    )
    assert res_none.status_code == 400


def test_syllabus_student_not_found(client):
    res = client.post(
        "/api/syllabus",
        json={"student_id": "nonexistent_student", "text": "Quadratic Equations"},
    )
    assert res.status_code == 404
    assert res.json()["code"] == "STUDENT_NOT_FOUND"


def test_graph_validation_cycle_and_missing_prereqs():
    # Missing prerequisite
    invalid_topics = [
        Topic(id="t1", name="Topic 1", prereq_ids=["non_existent"]),
    ]
    with pytest.raises(GraphValidationError):
        validate_topic_graph(invalid_topics)

    # Self loop
    self_loop = [
        Topic(id="t1", name="Topic 1", prereq_ids=["t1"]),
    ]
    with pytest.raises(GraphValidationError):
        validate_topic_graph(self_loop)

    # Direct cycle: t1 -> t2 -> t1
    cyclic = [
        Topic(id="t1", name="Topic 1", prereq_ids=["t2"]),
        Topic(id="t2", name="Topic 2", prereq_ids=["t1"]),
    ]
    with pytest.raises(GraphValidationError):
        validate_topic_graph(cyclic)


def test_idempotent_seeding_preserves_progress(client):
    res_st = client.post("/api/students", json={"name": "Progress Student", "lang": "en"})
    student_id = res_st.json()["student_id"]

    # Set some progress on quadratic_equations
    with get_db() as conn:
        conn.execute(
            """
            UPDATE topic_state
            SET mastery = 0.85, status = 'mastered'
            WHERE student_id = ? AND topic_id = 'quadratic_equations'
            """,
            (student_id,),
        )

    # Re-seed syllabus via API
    res = client.post(
        "/api/syllabus",
        json={"student_id": student_id, "goal": "Review math"},
    )
    assert res.status_code == 200

    # Verify progress was preserved
    graph_res = client.get(f"/api/graph/{student_id}")
    states = {s["topic_id"]: s for s in graph_res.json()["states"]}
    assert states["quadratic_equations"]["mastery"] == 0.85
    assert states["quadratic_equations"]["status"] == "mastered"
