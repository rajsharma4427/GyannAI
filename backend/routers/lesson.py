from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.contracts import Lesson, Topic, Lang
from backend.db import get_db
import ai_engine

router = APIRouter(prefix="/api/lesson", tags=["lesson"])


@router.get("/{student_id}/{topic_id}", response_model=Lesson)
def get_lesson(
    student_id: str,
    topic_id: str,
    lang: Optional[Lang] = Query(default=None),
):
    with get_db() as conn:
        student = conn.execute("SELECT id, lang FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        topic_row = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
        if not topic_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic '{topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
            )

        state_row = conn.execute(
            "SELECT gap_type FROM topic_state WHERE student_id = ? AND topic_id = ?",
            (student_id, topic_id),
        ).fetchone()

        gap_type = state_row["gap_type"] if state_row else None
        selected_lang = lang if lang else student["lang"]

        topic = Topic(
            id=topic_row["id"],
            name=topic_row["name"],
            parent_id=topic_row["parent_id"],
            description=topic_row["description"] or "",
        )

    try:
        lesson = ai_engine.explain_story(topic=topic, gap_type=gap_type, lang=selected_lang)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to generate lesson: {str(e)}", "code": "AI_ERROR"},
        )

    return lesson
