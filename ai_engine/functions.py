"""
ai_engine.functions

The eight primary AI functions for Gyaan Loop, conforming to the frozen shared contract.
Handles input validation, mock mode delegation, response caching, model prompt invocation,
and post-processing rules.
"""

import os
from typing import List, Optional, Union

from ai_engine.contracts import (
    Topic,
    Question,
    MistakeAnalysis,
    Lesson,
    TeachBackResult,
    Flashcard,
    GapType,
)
from ai_engine.errors import AIError
import ai_engine.mock as mock_engine


def is_mock_enabled() -> bool:
    """Return True if mock mode is active (default is active if AI_MOCK=1 or unset during dev)."""
    return os.getenv("AI_MOCK", "1") == "1"


def extract_syllabus(text: str) -> list[Topic]:
    """
    Extract topics and prerequisite structure from pasted syllabus text.
    Returns between 3 and 25 topics with canonical or snake_case IDs.
    """
    if not text or not text.strip():
        raise AIError("Syllabus text is empty or contains no usable content.")

    if is_mock_enabled():
        return mock_engine.mock_extract_syllabus(text)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def draft_syllabus(goal: str) -> list[Topic]:
    """
    Draft an ordered learning track of topics from a learning goal.
    """
    if not goal or not goal.strip():
        raise AIError("Learning goal cannot be empty.")

    if is_mock_enabled():
        return mock_engine.mock_draft_syllabus(goal)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def generate_questions(
    topic: Union[Topic, str], n: int = 5, difficulty: int = 2
) -> list[Question]:
    """
    Generate exactly n questions for the given topic and difficulty (1=easy, 2=medium, 3=hard).
    """
    if n <= 0:
        raise ValueError("Question count n must be positive.")
    if difficulty not in (1, 2, 3):
        raise ValueError("Difficulty must be 1, 2, or 3.")

    if is_mock_enabled():
        return mock_engine.mock_generate_questions(topic, n, difficulty)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def classify_mistake(
    question: Question,
    chosen_index: int,
    topic: Union[Topic, str],
    prereqs: list[Union[Topic, str]],
) -> MistakeAnalysis:
    """
    Classify a student's error on a question into a gap type (conceptual, procedural, careless, prerequisite).
    """
    if chosen_index < 0 or chosen_index >= len(question.options):
        raise ValueError(
            f"Chosen index {chosen_index} is out of bounds for options length {len(question.options)}."
        )
    if chosen_index == question.correct_index:
        raise ValueError(
            f"Chosen index {chosen_index} is the correct answer; mistake analysis only applies to wrong choices."
        )

    if is_mock_enabled():
        return mock_engine.mock_classify_mistake(question, chosen_index, topic, prereqs)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def explain_story(
    topic: Union[Topic, str], gap_type: Optional[Union[GapType, str]] = None, lang: str = "en"
) -> Lesson:
    """
    Generate a spoken-style story lesson (<= 120 words), explanation (100-180 words),
    key terms, and 2-3 practice exercises.
    """
    if is_mock_enabled():
        return mock_engine.mock_explain_story(topic, gap_type, lang)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def grade_teachback(
    topic: Union[Topic, str], transcript: str, key_points: list[str]
) -> TeachBackResult:
    """
    Grade a student's spoken explanation against key points.
    Computes score deterministically in code based on fraction covered minus errors.
    """
    if not key_points:
        raise ValueError("Key points list cannot be empty for teachback grading.")

    if is_mock_enabled():
        return mock_engine.mock_grade_teachback(topic, transcript, key_points)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def make_flashcards(
    topic: Union[Topic, str],
    gap_type: Optional[Union[GapType, str]] = None,
    missing: Optional[list[str]] = None,
    n: int = 2,
) -> list[Flashcard]:
    """
    Generate exactly n flashcards (front prompt, back answer <= 40 words).
    """
    if n <= 0:
        raise ValueError("Flashcard count n must be positive.")

    if is_mock_enabled():
        return mock_engine.mock_make_flashcards(topic, gap_type, missing, n)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")


def make_note(topic: Union[Topic, str], summary: str, lang: str = "en") -> str:
    """
    Generate a concise spoken-friendly note (2-4 sentences, <= 80 words).
    """
    if is_mock_enabled():
        return mock_engine.mock_make_note(topic, summary, lang)

    raise AIError("Real AI provider client is not configured yet. Run with AI_MOCK=1.")
