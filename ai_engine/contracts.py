"""
ai_engine.contracts

Authoritative contract models re-exported for the AI Engine.
Provides canonical models and canonical prerequisite structure.
"""

from backend.contracts import (
    Topic,
    Question,
    MistakeAnalysis,
    Lesson,
    TeachBackResult,
    Flashcard,
    Note,
    TopicState,
    Lang,
    GapType,
)

# Canonical Topic IDs and Prerequisites (Class 10 Quadratic Equations Track)
CANONICAL_PREREQUISITES: dict[str, list[str]] = {
    "integers": [],
    "fractions": [],
    "algebraic_expressions": ["integers"],
    "linear_equations": ["algebraic_expressions", "fractions"],
    "exponents": ["integers"],
    "polynomials": ["algebraic_expressions", "exponents"],
    "factorization": ["polynomials"],
    "identities": ["polynomials", "exponents"],
    "square_roots": ["exponents"],
    "quadratic_equations": ["polynomials", "linear_equations"],
    "solve_by_factorization": ["quadratic_equations", "factorization"],
    "quadratic_formula": ["quadratic_equations", "square_roots"],
    "discriminant": ["quadratic_formula"],
}

__all__ = [
    "Topic",
    "Question",
    "MistakeAnalysis",
    "Lesson",
    "TeachBackResult",
    "Flashcard",
    "Note",
    "TopicState",
    "Lang",
    "GapType",
    "CANONICAL_PREREQUISITES",
]
