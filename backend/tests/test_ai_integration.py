"""
backend.tests.test_ai_integration

Comprehensive integration tests between Person 1's AI Engine and Person 2's FastAPI Backend.
Verifies all 13 integration points defined in Section 8 of the integration specification.
"""

import inspect
import pytest
from fastapi.testclient import TestClient

import ai_engine
from ai_engine.errors import AIError
from backend.contracts import (
    Topic,
    Question,
    MistakeAnalysis,
    Lesson,
    TeachBackResult,
    Flashcard,
    Note,
    TopicState,
)
from backend.db import get_db
from backend.main import app


def test_1_all_eight_ai_engine_functions_imported():
    """Verify all 8 functions and AIError are properly exposed by ai_engine."""
    expected_attrs = [
        "extract_syllabus",
        "draft_syllabus",
        "generate_questions",
        "classify_mistake",
        "explain_story",
        "grade_teachback",
        "make_flashcards",
        "make_note",
        "AIError",
    ]
    for attr in expected_attrs:
        assert hasattr(ai_engine, attr), f"ai_engine missing {attr}"


def test_2_public_signatures_preserved():
    """Verify exact public function signatures."""
    sig_gen = inspect.signature(ai_engine.generate_questions)
    assert "topic" in sig_gen.parameters
    assert "n" in sig_gen.parameters
    assert "difficulty" in sig_gen.parameters

    sig_class = inspect.signature(ai_engine.classify_mistake)
    assert list(sig_class.parameters.keys()) == ["question", "chosen_index", "topic", "prereqs"]

    sig_exp = inspect.signature(ai_engine.explain_story)
    assert "topic" in sig_exp.parameters
    assert "gap_type" in sig_exp.parameters
    assert "lang" in sig_exp.parameters

    sig_tb = inspect.signature(ai_engine.grade_teachback)
    assert list(sig_tb.parameters.keys()) == ["topic", "transcript", "key_points"]

    sig_fc = inspect.signature(ai_engine.make_flashcards)
    assert "topic" in sig_fc.parameters
    assert "gap_type" in sig_fc.parameters
    assert "missing" in sig_fc.parameters
    assert "n" in sig_fc.parameters

    sig_note = inspect.signature(ai_engine.make_note)
    assert list(sig_note.parameters.keys()) == ["topic", "summary", "lang"]


def test_3_accepts_authoritative_model_types():
    """Verify functions accept authoritative Topic and Question model instances."""
    topic = Topic(id="quadratic_equations", name="Quadratic Equations", prereq_ids=["factorization"])
    questions = ai_engine.generate_questions(topic, n=2, difficulty=2)
    assert len(questions) == 2
    assert all(isinstance(q, Question) for q in questions)

    q = questions[0]
    wrong_idx = (q.correct_index + 1) % 4
    prereqs = [Topic(id="factorization", name="Factorization", prereq_ids=[])]

    analysis = ai_engine.classify_mistake(q, wrong_idx, topic, prereqs)
    assert isinstance(analysis, MistakeAnalysis)

    lesson = ai_engine.explain_story(topic, gap_type="conceptual", lang="en")
    assert isinstance(lesson, Lesson)

    tb = ai_engine.grade_teachback(topic, "Quadratic roots require factor pairs and formula", ["key concept"])
    assert isinstance(tb, TeachBackResult)

    cards = ai_engine.make_flashcards(topic, gap_type="conceptual", missing=["root definition"], n=2)
    assert len(cards) == 2
    assert all(isinstance(c, Flashcard) for c in cards)

    note = ai_engine.make_note(topic, "Mastered discriminant formula", lang="en")
    assert isinstance(note, str)


def test_4_generated_topics_and_questions_validate():
    """Verify topics and questions strictly validate against the authoritative contract."""
    topics = ai_engine.extract_syllabus("Class 10 CBSE Math Syllabus")
    for t in topics:
        assert isinstance(t, Topic)
        assert t.id
        assert t.name
        assert isinstance(t.prereq_ids, list)

    questions = ai_engine.generate_questions("solve_by_factorization", n=3, difficulty=2)
    for q in questions:
        assert isinstance(q, Question)
        assert q.topic_id == "solve_by_factorization"
        assert q.stem
        assert len(q.options) == 4
        assert len(set(q.options)) == 4
        assert 0 <= q.correct_index < 4
        assert len(q.misconception_tags) == 3


def test_5_mistake_classification_maps_prereq_id():
    """Verify mistake classification sets suspected_prereq_id properly."""
    q = Question(
        id="q1",
        topic_id="quadratic_equations",
        stem="Solve x^2 - 4 = 0",
        options=["x = +-2", "x = 4", "x = -4", "x = 0"],
        correct_index=0,
        difficulty=1,
    )
    prereqs = [Topic(id="square_roots", name="Square Roots", prereq_ids=[])]
    analysis = ai_engine.classify_mistake(q, 1, "quadratic_equations", prereqs)

    assert analysis.gap_type == "prerequisite"
    assert analysis.suspected_prereq_id == "square_roots"
    # Backwards compatibility check
    assert analysis.suspected_prerequisite_id == "square_roots"

    # Empty prereqs downgrade to conceptual
    analysis_no_prereqs = ai_engine.classify_mistake(q, 1, "quadratic_equations", [])
    assert analysis_no_prereqs.gap_type == "conceptual"
    assert analysis_no_prereqs.suspected_prereq_id is None


def test_6_lessons_validate_and_contain_valid_exercises():
    """Verify lessons contain valid exercises matching Question contract."""
    lesson = ai_engine.explain_story("factorization", gap_type="procedural", lang="en")
    assert isinstance(lesson, Lesson)
    assert len(lesson.story.split()) <= 120
    assert len(lesson.exercises) >= 2
    for ex in lesson.exercises:
        assert isinstance(ex, Question)
        assert ex.topic_id == "factorization"
        assert ex.stem
        assert len(ex.options) == 4


def test_7_teachback_results_validate():
    """Verify teachback results match schema and score clamped to [0.0, 1.0]."""
    key_points = ["Definition of discriminant", "b^2 - 4ac formula"]
    result = ai_engine.grade_teachback(
        "discriminant",
        "The discriminant is calculated using b squared minus 4ac.",
        key_points,
    )
    assert isinstance(result, TeachBackResult)
    assert 0.0 <= result.score <= 1.0
    assert set(result.covered + result.missing) == set(key_points)


def test_8_flashcards_contain_required_fields():
    """Verify flashcards have required topic_id and valid source."""
    cards = ai_engine.make_flashcards("integers", gap_type="conceptual", missing=["negative sign rules"], n=2)
    for c in cards:
        assert isinstance(c, Flashcard)
        assert c.id
        assert c.topic_id == "integers"
        assert c.front
        assert c.back
        assert len(c.back.split()) <= 40
        assert c.source in ("gap", "teachback")


def test_9_notes_generation_and_storage(client):
    """Verify notes can be generated and persisted via the backend."""
    st = client.post("/api/students", json={"name": "Note Tester", "lang": "en"}).json()
    sid = st["student_id"]

    note_body = ai_engine.make_note("polynomials", "Student understands degrees and leading coefficients", lang="en")
    assert isinstance(note_body, str)
    assert len(note_body.split()) <= 80

    res = client.post(
        "/api/notes",
        json={"student_id": sid, "topic_id": "polynomials", "body": note_body},
    )
    assert res.status_code == 201

    notes_list = client.get(f"/api/notes/{sid}/polynomials").json()["notes"]
    assert len(notes_list) >= 1
    assert notes_list[0]["body"] == note_body


def test_10_backend_endpoints_calling_ai_return_valid_shapes(client):
    """Verify backend endpoints calling AI functions return contract-shaped responses."""
    # 1. Create student
    st = client.post("/api/students", json={"name": "Integration Student", "lang": "en"}).json()
    sid = st["student_id"]

    # 2. Syllabus extraction & drafting
    syl = client.post("/api/syllabus", json={"student_id": sid, "goal": "Class 10 Math"}).json()
    assert "topics" in syl
    assert len(syl["topics"]) >= 13

    # 3. Lesson endpoint calling explain_story
    lesson_res = client.get(f"/api/lesson/{sid}/quadratic_equations")
    assert lesson_res.status_code == 200
    lesson_data = lesson_res.json()
    assert "story" in lesson_data
    assert "exercises" in lesson_data

    # 4. Teachback endpoint calling grade_teachback, make_flashcards, make_note
    tb_res = client.post(
        "/api/teachback",
        json={
            "student_id": sid,
            "topic_id": "quadratic_equations",
            "transcript": "Quadratic equations model parabolic paths using standard form ax^2+bx+c=0.",
        },
    )
    assert tb_res.status_code == 200
    tb_data = tb_res.json()
    assert "result" in tb_data
    assert "flashcards" in tb_data
    assert "note" in tb_data
    assert "state" in tb_data


def test_11_ai_failures_produce_structured_errors(client, monkeypatch):
    """Verify AI failure produces safe HTTP 500 error with code AI_ERROR."""
    st = client.post("/api/students", json={"name": "Failure Student", "lang": "en"}).json()
    sid = st["student_id"]

    def failing_explain(*args, **kwargs):
        raise AIError("AI service temporarily unavailable")

    monkeypatch.setattr(ai_engine, "explain_story", failing_explain)

    res = client.get(f"/api/lesson/{sid}/quadratic_equations")
    assert res.status_code == 500
    assert res.json()["code"] == "AI_ERROR"


def test_12_sqlite_state_rollback_on_failed_operation(client, monkeypatch):
    """Verify that an AI failure in teachback aborts without corrupting or partially writing data."""
    st = client.post("/api/students", json={"name": "Rollback Student", "lang": "en"}).json()
    sid = st["student_id"]

    # Ensure make_flashcards fails after grading
    def failing_flashcards(*args, **kwargs):
        raise AIError("Flashcard generation failed unexpectedly")

    monkeypatch.setattr(ai_engine, "make_flashcards", failing_flashcards)

    res = client.post(
        "/api/teachback",
        json={
            "student_id": sid,
            "topic_id": "quadratic_equations",
            "transcript": "Good explanation about quadratic equations.",
        },
    )
    assert res.status_code == 500
    assert res.json()["code"] == "AI_ERROR"

    # Verify no teachback was committed
    db_path = client.app.state._db_path if hasattr(client.app.state, "_db_path") else None
    with get_db(db_path) as conn:
        tb_count = conn.execute("SELECT count(*) as cnt FROM teachbacks WHERE student_id = ?", (sid,)).fetchone()["cnt"]
        fc_count = conn.execute("SELECT count(*) as cnt FROM flashcards WHERE student_id = ?", (sid,)).fetchone()["cnt"]
        assert tb_count == 0
        assert fc_count == 0


def test_13_backend_starts_with_ai_mock_and_no_key(monkeypatch):
    """Verify backend starts cleanly in mock mode without ANTHROPIC_API_KEY."""
    monkeypatch.setenv("AI_MOCK", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from backend.main import app as test_app
    with TestClient(test_app) as c:
        health_res = c.get("/docs")
        assert health_res.status_code == 200
