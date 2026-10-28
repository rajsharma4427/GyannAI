import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status

from backend.contracts import CreateNoteRequest, NotesListResponse, Note
from backend.db import get_db, record_activity
from backend.engine import clock

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("/{student_id}/{topic_id}", response_model=NotesListResponse)
def get_notes(student_id: str, topic_id: str):
    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        topic = conn.execute("SELECT id FROM topics WHERE id = ?", (topic_id,)).fetchone()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic '{topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
            )

        rows = conn.execute(
            """
            SELECT id, topic_id, author, body, created_at
            FROM notes
            WHERE student_id = ? AND topic_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (student_id, topic_id),
        ).fetchall()

        notes = [
            Note(
                id=r["id"],
                topic_id=r["topic_id"],
                author=r["author"],
                body=r["body"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    return NotesListResponse(notes=notes)


@router.post("", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(req: CreateNoteRequest):
    if not req.body or not req.body.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Note body cannot be empty", "code": "EMPTY_BODY"},
        )

    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (req.student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{req.student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        topic = conn.execute("SELECT id FROM topics WHERE id = ?", (req.topic_id,)).fetchone()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic '{req.topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
            )

        note_id = f"note_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """
            INSERT INTO notes (id, student_id, topic_id, author, body, created_at)
            VALUES (?, ?, ?, 'student', ?, ?)
            """,
            (note_id, req.student_id, req.topic_id, req.body.strip(), now_iso),
        )

        today_str = clock.today(conn)
        record_activity(conn, req.student_id, today_str)

    return Note(
        id=note_id,
        topic_id=req.topic_id,
        author="student",
        body=req.body.strip(),
        created_at=now_iso,
    )
