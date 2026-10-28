"""
Unit tests for ai_engine functions and mock mode.
Verifies contract types, input validation, and business rules offline without network or API key.
"""

import pytest

from ai_engine import (
    extract_syllabus,
    draft_syllabus,
    generate_questions,
    classify_mistake,
    explain_story,
    grade_teachback,
    make_flashcards,
    make_note,
    AIError,
)
from ai_engine.contracts import (
    Topic,
    Question,
    MistakeAnalysis,
    Lesson,
    TeachBackResult,
    Flashcard,
    CANONICAL_PREREQUISITES,
)


def test_top_level_exports():
    """Verify that ai_engine exports exactly the contract functions and AIError."""
    import ai_engine
    expected_exports = {
        "extract_syllabus",
        "draft_syllabus",
        "generate_questions",
        "classify_mistake",
        "explain_story",
        "grade_teachback",
        "make_flashcards",
        "make_note",
        "AIError",
    }
    assert set(ai_engine.__all__) == expected_exports


def test_extract_syllabus_mock():
    """Verify extract_syllabus returns valid canonical Topic list."""
    topics = extract_syllabus("Sample Class 10 Math Syllabus")
    assert isinstance(topics, list)
    assert len(topics) == 13
    assert all(isinstance(t, Topic) for t in topics)

    # Check canonical topic IDs
    topic_ids = [t.id for t in topics]
    for canonical_id in CANONICAL_PREREQUISITES:
        assert canonical_id in topic_ids

    # Check quadratic_equations prerequisites
    quad = next(t for t in topics if t.id == "quadratic_equations")
    assert set(quad.prerequisites) == {"polynomials", "linear_equations"}

    # Check descriptions are multi-sentence (used for teach-back rubric)
    for t in topics:
        assert len(t.description.split(".")) >= 2


def test_extract_syllabus_empty():
    """Empty text should raise AIError."""
    with pytest.raises(AIError):
        extract_syllabus("   ")


def test_draft_syllabus_mock():
    """Verify draft_syllabus returns valid sequenced learning track."""
    # For Class 10 track: returns canonical 13 topics per contract section 7.8
    track = draft_syllabus("Prepare for Class 10 Quadratic Equations")
    assert isinstance(track, list)
    assert len(track) == 13
    assert all(isinstance(t, Topic) for t in track)

    # For general goal: returns 5 topics
    track_sql = draft_syllabus("Learn SQL Fundamentals")
    assert isinstance(track_sql, list)
    assert len(track_sql) == 5
    seen_ids = set()
    for t in track_sql:
        assert t.id not in seen_ids
        for prereq in t.prerequisites:
            assert prereq in seen_ids
        seen_ids.add(t.id)


def test_draft_syllabus_empty():
    """Empty goal should raise AIError."""
    with pytest.raises(AIError):
        draft_syllabus("")


def test_generate_questions_mock():
    """Verify generate_questions produces n questions with four distinct options and varied correct answers."""
    n = 5
    diff = 2
    questions = generate_questions("quadratic_equations", n=n, difficulty=diff)

    assert len(questions) == n
    correct_positions = set()

    for i, q in enumerate(questions):
        assert isinstance(q, Question)
        assert q.topic_id == "quadratic_equations"
        assert q.difficulty == diff
        assert len(q.options) == 4
        # All options distinct
        assert len(set(q.options)) == 4
        # Correct index is within range
        assert 0 <= q.correct_index < 4
        correct_positions.add(q.correct_index)
        # Misconception tags: one for each of the 3 wrong options
        assert len(q.misconception_tags) == 3

    # Varied correct positions across questions
    assert len(correct_positions) > 1


def test_generate_questions_validation():
    """Verify programmer input errors raise ValueError."""
    with pytest.raises(ValueError):
        generate_questions("quadratic_equations", n=0, difficulty=1)

    with pytest.raises(ValueError):
        generate_questions("quadratic_equations", n=3, difficulty=4)


def test_classify_mistake_with_prereqs():
    """When prerequisites are present, classify_mistake returns prerequisite gap."""
    questions = generate_questions("quadratic_equations", n=1, difficulty=2)
    q = questions[0]
    wrong_idx = (q.correct_index + 1) % 4

    prereqs = ["factorization", "polynomials"]
    result = classify_mistake(q, wrong_idx, "quadratic_equations", prereqs)

    assert isinstance(result, MistakeAnalysis)
    assert result.gap_type == "prerequisite"
    assert result.suspected_prerequisite_id == "factorization"
    assert len(result.reason) > 5


def test_classify_mistake_without_prereqs():
    """When prerequisites are empty, result is downgraded to conceptual."""
    questions = generate_questions("quadratic_equations", n=1, difficulty=1)
    q = questions[0]
    wrong_idx = (q.correct_index + 1) % 4

    result = classify_mistake(q, wrong_idx, "quadratic_equations", [])

    assert isinstance(result, MistakeAnalysis)
    assert result.gap_type == "conceptual"
    assert result.suspected_prerequisite_id is None
    assert len(result.reason) > 5


def test_classify_mistake_validation():
    """Verify invalid index or correct index raises ValueError."""
    questions = generate_questions("quadratic_equations", n=1, difficulty=1)
    q = questions[0]

    # Picking the correct answer is a programmer error
    with pytest.raises(ValueError):
        classify_mistake(q, q.correct_index, "quadratic_equations", ["factorization"])

    # Out of bounds indices
    with pytest.raises(ValueError):
        classify_mistake(q, -1, "quadratic_equations", [])
    with pytest.raises(ValueError):
        classify_mistake(q, 4, "quadratic_equations", [])


def test_explain_story_mock():
    """Verify explain_story returns a valid Lesson under 120 words for story with 2 exercises."""
    for lang in ("en", "hi", "hinglish"):
        lesson = explain_story("quadratic_equations", gap_type="conceptual", lang=lang)
        assert isinstance(lesson, Lesson)
        assert lesson.topic_id == "quadratic_equations"

        # Story word count must be <= 120 words
        story_words = len(lesson.story.split())
        assert story_words <= 120

        # Key terms: 3 to 6
        assert 3 <= len(lesson.key_terms) <= 6

        # Exercises: 2 valid questions
        assert len(lesson.exercises) == 2
        for ex in lesson.exercises:
            assert isinstance(ex, Question)
            assert len(ex.options) == 4
            assert len(ex.misconception_tags) == 3


def test_grade_teachback_mock():
    """Verify deterministic teachback grading with word overlap and exact key points partition."""
    key_points = [
        "Standard quadratic equation form is ax squared plus bx plus c equals zero",
        "The coefficient of x squared cannot equal zero",
        "Factorization splits the middle term using factor pairs",
        "Zero product property states if product is zero at least one factor is zero",
    ]

    transcript = (
        "In a quadratic equation we have ax squared plus bx plus c equals zero. "
        "Also the coefficient of x squared cannot be zero. "
        "And we use the zero product property to find roots."
    )

    result = grade_teachback("quadratic_equations", transcript, key_points)
    assert isinstance(result, TeachBackResult)
    assert result.topic_id == "quadratic_equations"

    # Covered + missing must equal key points exactly
    assert set(result.covered + result.missing) == set(key_points)
    assert len(result.covered) + len(result.missing) == len(key_points)

    # Score calculation check
    expected_score = round(len(result.covered) / len(key_points), 2)
    assert result.score == expected_score
    assert 0.0 <= result.score <= 1.0
    assert len(result.feedback) > 10


def test_grade_teachback_short_transcript():
    """Transcript with < 3 words returns deterministic 0 score with all missing."""
    key_points = ["Key point 1", "Key point 2"]
    result = grade_teachback("quadratic_equations", "hello there", key_points)

    assert result.score == 0.0
    assert result.covered == []
    assert result.missing == key_points
    assert "detail" in result.feedback.lower()


def test_grade_teachback_empty_keypoints():
    """Empty key points raises ValueError."""
    with pytest.raises(ValueError):
        grade_teachback("quadratic_equations", "Long student transcript here", [])


def test_make_flashcards_mock():
    """Verify make_flashcards produces exactly n cards with correct sources."""
    # When missing points exist -> source is 'teachback'
    missing = ["Coefficient a cannot be zero", "Discriminant determines root nature"]
    cards_tb = make_flashcards("quadratic_equations", "conceptual", missing, n=4)
    assert len(cards_tb) == 4
    for c in cards_tb:
        assert isinstance(c, Flashcard)
        assert c.source == "teachback"
        assert len(c.back.split()) <= 40

    # When missing points empty -> source is 'gap'
    cards_gap = make_flashcards("quadratic_equations", "procedural", [], n=3)
    assert len(cards_gap) == 3
    for c in cards_gap:
        assert isinstance(c, Flashcard)
        assert c.source == "gap"
        assert len(c.back.split()) <= 40

    # Count <= 0 raises ValueError
    with pytest.raises(ValueError):
        make_flashcards("quadratic_equations", "conceptual", [], n=0)


def test_make_note_mock():
    """Verify make_note returns concise string under 80 words without markdown headings."""
    for lang in ("en", "hi", "hinglish"):
        note = make_note("quadratic_equations", "Student mastered factorization", lang=lang)
        assert isinstance(note, str)
        assert len(note.split()) <= 80
        assert "#" not in note
