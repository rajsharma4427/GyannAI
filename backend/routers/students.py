import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from backend.contracts import CreateStudentRequest, CreateStudentResponse
from backend.db import get_db

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post("", response_model=CreateStudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(req: CreateStudentRequest):
    if not req.name or not req.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Student name cannot be empty", "code": "INVALID_NAME"},
        )
    if req.lang not in ("en", "hi", "hinglish"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Invalid language '{req.lang}'", "code": "INVALID_LANGUAGE"},
        )

    student_id = f"student_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        conn.execute(
            "INSERT INTO students (id, name, lang, created_at) VALUES (?, ?, ?, ?)",
            (student_id, req.name.strip(), req.lang, now_iso),
        )

        # Initialize topic_state for existing topics
        topics = conn.execute("SELECT id FROM topics").fetchall()
        for t in topics:
            conn.execute(
                """
                INSERT OR IGNORE INTO topic_state (
                    student_id, topic_id, mastery, confidence, gap_type,
                    interval_days, ease, next_review, status, repetitions, attempts_count
                )
                VALUES (?, ?, 0.0, 0.0, NULL, 0, 2.5, NULL, 'unseen', 0, 0)
                """,
                (student_id, t["id"]),
            )

    return CreateStudentResponse(student_id=student_id)
