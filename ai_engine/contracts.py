"""
ai_engine.contracts

Shared data models for Gyaan Loop (Section 3 shared contract).
Note: When backend/contracts.py is created by Person 2, keep these models in exact 1:1 sync.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator


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


class Topic(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    parent_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_name_or_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "title" not in data and "name" in data:
                data["title"] = data["name"]
        return data

    @property
    def name(self) -> str:
        return self.title


class Question(BaseModel):
    id: str
    topic_id: str
    text: str
    options: list[str]
    correct_index: int
    misconception_tags: list[str] = Field(default_factory=list)
    difficulty: int
    explanation: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_question_or_text(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "text" not in data and "question" in data:
                data["text"] = data["question"]
            elif "question" not in data and "text" in data:
                data["question"] = data["text"]
        return data

    @property
    def question(self) -> str:
        return self.text


class MistakeAnalysis(BaseModel):
    gap_type: str  # 'conceptual' | 'procedural' | 'careless' | 'prerequisite'
    suspected_prerequisite_id: Optional[str] = None
    reason: str


class Lesson(BaseModel):
    topic_id: str
    story: str
    explanation: str
    key_terms: list[str] = Field(default_factory=list)
    exercises: list[Question] = Field(default_factory=list)


class TeachBackResult(BaseModel):
    topic_id: str
    score: float
    covered: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    feedback: str


class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    source: str = "gap"  # 'teachback' | 'gap'
    topic_id: Optional[str] = None
