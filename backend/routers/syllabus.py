from fastapi import APIRouter, HTTPException, status
from backend.contracts import CreateSyllabusRequest, SyllabusResponse, Topic
from backend.db import get_db
from backend.engine.backtrace import validate_topic_graph, GraphValidationError
import ai_engine

router = APIRouter(prefix="/api/syllabus", tags=["syllabus"])


@router.post("", response_model=SyllabusResponse)
def create_syllabus(req: CreateSyllabusRequest):
    has_text = bool(req.text and req.text.strip())
    has_goal = bool(req.goal and req.goal.strip())

    if (has_text and has_goal) or (not has_text and not has_goal):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Exactly one of 'text' or 'goal' must be supplied",
                "code": "INVALID_INPUT",
            },
        )

    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (req.student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{req.student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

    try:
        if has_text:
            topics: list[Topic] = ai_engine.extract_syllabus(req.text.strip())
        else:
            topics = ai_engine.draft_syllabus(req.goal.strip())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"AI syllabus extraction failed: {str(e)}", "code": "AI_ERROR"},
        )

    try:
        validate_topic_graph(topics)
    except GraphValidationError as gve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Invalid topic graph generated: {str(gve)}", "code": "INVALID_GRAPH"},
        )

    with get_db() as conn:
        for t in topics:
            conn.execute(
                """
                INSERT INTO topics (id, name, parent_id, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    parent_id = excluded.parent_id,
                    description = excluded.description
                """,
                (t.id, t.name, t.parent_id, t.description),
            )
            for prereq_id in t.prereq_ids:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO topic_prereqs (topic_id, prereq_id)
                    VALUES (?, ?)
                    """,
                    (t.id, prereq_id),
                )
            # Initialize TopicState for student without erasing existing progress
            conn.execute(
                """
                INSERT OR IGNORE INTO topic_state (
                    student_id, topic_id, mastery, confidence, gap_type,
                    interval_days, ease, next_review, status, repetitions, attempts_count
                )
                VALUES (?, ?, 0.0, 0.0, NULL, 0, 2.5, NULL, 'unseen', 0, 0)
                """,
                (req.student_id, t.id),
            )

    return SyllabusResponse(topics=topics)
