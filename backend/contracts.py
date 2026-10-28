"""
backend.contracts

Authoritative shared data models for Gyaan Loop REST API and AI Engine.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, model_validator

Lang = Literal["en", "hi", "hinglish"]
GapType = Literal["conceptual", "procedural", "careless", "prerequisite"]


class Topic(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    prereq_ids: list[str] = Field(default_factory=list)
    description: str = ""

    @model_validator(mode="before")
    @classmethod
    def handle_compat_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" not in data and "title" in data:
                data["name"] = data["title"]
            if "prereq_ids" not in data and "prerequisites" in data:
                data["prereq_ids"] = data["prerequisites"]
        return data

    @property
    def title(self) -> str:
        return self.name

    @property
    def prerequisites(self) -> list[str]:
        return self.prereq_ids


class Question(BaseModel):
    id: str
    topic_id: str
    stem: str
    options: list[str]
    correct_index: int
    difficulty: int
    misconception_tags: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def handle_compat_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "stem" not in data and "text" in data:
                data["stem"] = data["text"]
            elif "stem" not in data and "question" in data:
                data["stem"] = data["question"]
        return data

    @property
    def text(self) -> str:
        return self.stem

    @property
    def question(self) -> str:
        return self.stem


class MistakeAnalysis(BaseModel):
    gap_type: GapType
    suspected_prereq_id: Optional[str] = None
    reason: str

    @model_validator(mode="before")
    @classmethod
    def handle_compat_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "suspected_prereq_id" not in data and "suspected_prerequisite_id" in data:
                data["suspected_prereq_id"] = data["suspected_prerequisite_id"]
        return data

    @property
    def suspected_prerequisite_id(self) -> Optional[str]:
        return self.suspected_prereq_id


class Lesson(BaseModel):
    topic_id: str
    story: str
    explanation: str
    key_terms: list[str]
    exercises: list[Question]


class TeachBackResult(BaseModel):
    topic_id: str
    score: float
    covered: list[str]
    missing: list[str]
    errors: list[str]
    feedback: str


class Flashcard(BaseModel):
    id: str
    topic_id: str
    front: str
    back: str
    source: Literal["gap", "teachback"]


class Note(BaseModel):
    id: str
    topic_id: str
    author: Literal["ai", "student"]
    body: str
    created_at: str


class TopicState(BaseModel):
    topic_id: str
    mastery: float
    confidence: float
    gap_type: Optional[GapType] = None
    interval_days: int = 0
    ease: float = 2.5
    next_review: Optional[str] = None
    status: Literal["unseen", "gap", "learning", "mastered"] = "unseen"


# ---------------------------------------------------------
# Request & Response Models for REST API
# ---------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    code: str


class CreateStudentRequest(BaseModel):
    name: str
    lang: Lang = "en"


class CreateStudentResponse(BaseModel):
    student_id: str


class CreateSyllabusRequest(BaseModel):
    student_id: str
    text: Optional[str] = None
    goal: Optional[str] = None


class SyllabusResponse(BaseModel):
    topics: list[Topic]


class GraphResponse(BaseModel):
    topics: list[Topic]
    states: list[TopicState]


class DiagnosticStartRequest(BaseModel):
    student_id: str
    topic_id: str


class DiagnosticStartResponse(BaseModel):
    session_id: str
    question: Question


class DiagnosticAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    chosen_index: int
    time_ms: int = 0


class BacktraceInfo(BaseModel):
    from_topic_id: str
    to_topic_id: str
    reason: str


class GapItem(BaseModel):
    topic_id: str
    gap_type: GapType


class DiagnosticSummary(BaseModel):
    gaps: list[GapItem]


class DiagnosticAnswerResponse(BaseModel):
    correct: bool
    done: bool
    next_question: Optional[Question] = None
    backtrace: Optional[BacktraceInfo] = None
    summary: Optional[DiagnosticSummary] = None


class TeachBackRequest(BaseModel):
    student_id: str
    topic_id: str
    transcript: str


class TeachBackResponse(BaseModel):
    result: TeachBackResult
    flashcards: list[Flashcard]
    note: Note
    state: TopicState


class DueFlashcardsResponse(BaseModel):
    cards: list[Flashcard]


class FlashcardReviewRequest(BaseModel):
    student_id: str
    card_id: str
    quality: int


class FlashcardReviewResponse(BaseModel):
    state: TopicState


class CreateNoteRequest(BaseModel):
    student_id: str
    topic_id: str
    body: str


class NotesListResponse(BaseModel):
    notes: list[Note]


class WeakestTopic(BaseModel):
    topic_id: str
    mastery: float


class DashboardResponse(BaseModel):
    overall_mastery: float
    topics_mastered: int
    topics_total: int
    due_today: int
    streak_days: int
    weakest: list[WeakestTopic]


class AdvanceDaysRequest(BaseModel):
    student_id: str
    days: int


class AdvanceDaysResponse(BaseModel):
    new_date: str
