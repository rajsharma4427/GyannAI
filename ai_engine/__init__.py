"""
ai_engine

Standalone AI Engine for Gyaan Loop.
Exports the eight primary AI functions and the AIError exception.
"""

from ai_engine.errors import AIError
from ai_engine.functions import (
    extract_syllabus,
    draft_syllabus,
    generate_questions,
    classify_mistake,
    explain_story,
    grade_teachback,
    make_flashcards,
    make_note,
)

__all__ = [
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
