import pytest
from pydantic import ValidationError
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


def test_topic_model_validation():
    topic = Topic(id="algebra", name="Algebra", prereq_ids=["integers"])
    assert topic.id == "algebra"
    assert topic.name == "Algebra"
    assert topic.prereq_ids == ["integers"]
    assert topic.parent_id is None
    assert topic.description == ""

    # Defaults
    t2 = Topic(id="geom", name="Geometry")
    assert t2.prereq_ids == []


def test_question_model_validation():
    q = Question(
        id="q1",
        topic_id="algebra",
        stem="What is x?",
        options=["1", "2", "3", "4"],
        correct_index=0,
        difficulty=2,
    )
    assert q.id == "q1"
    assert len(q.options) == 4
    assert q.difficulty == 2
    assert q.misconception_tags == []


def test_mistake_analysis_validation():
    m = MistakeAnalysis(
        gap_type="prerequisite",
        suspected_prereq_id="integers",
        reason="Needs integers practice",
    )
    assert m.gap_type == "prerequisite"
    assert m.suspected_prereq_id == "integers"

    with pytest.raises(ValidationError):
        MistakeAnalysis(gap_type="invalid_gap", reason="Bad")


def test_lesson_model_validation():
    q = Question(
        id="q1",
        topic_id="t1",
        stem="Stem",
        options=["a", "b", "c", "d"],
        correct_index=1,
        difficulty=1,
    )
    lesson = Lesson(
        topic_id="t1",
        story="Once upon a time...",
        explanation="Here is how it works...",
        key_terms=["term1", "term2"],
        exercises=[q],
    )
    assert lesson.topic_id == "t1"
    assert len(lesson.exercises) == 1


def test_teachback_result_validation():
    tb = TeachBackResult(
        topic_id="t1",
        score=0.85,
        covered=["c1"],
        missing=["m1"],
        errors=[],
        feedback="Well done",
    )
    assert tb.score == 0.85
    assert tb.covered == ["c1"]


def test_flashcard_validation():
    card = Flashcard(
        id="c1",
        topic_id="t1",
        front="Q?",
        back="A!",
        source="teachback",
    )
    assert card.source == "teachback"

    with pytest.raises(ValidationError):
        Flashcard(id="c2", topic_id="t1", front="Q", back="A", source="other")


def test_note_validation():
    note = Note(
        id="n1",
        topic_id="t1",
        author="student",
        body="My note",
        created_at="2026-10-28T10:00:00",
    )
    assert note.author == "student"

    with pytest.raises(ValidationError):
        Note(id="n2", topic_id="t1", author="teacher", body="hi", created_at="2026-10-28")


def test_topic_state_validation():
    state = TopicState(
        topic_id="t1",
        mastery=0.75,
        confidence=0.5,
    )
    assert state.status == "unseen"
    assert state.interval_days == 0
    assert state.ease == 2.5
    assert state.next_review is None
