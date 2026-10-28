import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status

from backend.contracts import (
    TeachBackRequest,
    TeachBackResponse,
    TeachBackResult,
    Flashcard,
    Note,
    TopicState,
    Topic,
)
from backend.db import get_db, dumps_json, loads_json, record_activity
from backend.engine import clock
from backend.engine.mastery import (
    update_mastery_on_teachback,
    update_confidence,
    calculate_status,
)
import ai_engine

router = APIRouter(prefix="/api/teachback", tags=["teachback"])


@router.post("", response_model=TeachBackResponse)
def submit_teachback(req: TeachBackRequest):
    if not req.transcript or not req.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Transcript cannot be empty", "code": "EMPTY_TRANSCRIPT"},
        )

    with get_db() as conn:
        student = conn.execute("SELECT id, lang FROM students WHERE id = ?", (req.student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{req.student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        topic_row = conn.execute("SELECT * FROM topics WHERE id = ?", (req.topic_id,)).fetchone()
        if not topic_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic '{req.topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
            )

        state_row = conn.execute(
            "SELECT * FROM topic_state WHERE student_id = ? AND topic_id = ?",
            (req.student_id, req.topic_id),
        ).fetchone()

        old_mastery = state_row["mastery"] if state_row else 0.0
        old_conf = state_row["confidence"] if state_row else 0.0
        gap_type = state_row["gap_type"] if state_row else None

        topic = Topic(
            id=topic_row["id"],
            name=topic_row["name"],
            parent_id=topic_row["parent_id"],
            description=topic_row["description"] or "",
        )

        # 2. Key reference points from canonical description and topic concept
        key_points = [
            f"Definition and principles of {topic.name}",
            f"Application of {topic.name} in problem solving",
            "Core algebraic manipulation and verification",
        ]
        if topic.description:
            key_points.append(topic.description[:80])

        # 3. Call AI engine to grade teachback
        try:
            result: TeachBackResult = ai_engine.grade_teachback(
                topic=topic,
                transcript=req.transcript.strip(),
                key_points=key_points,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": f"Teach-back grading failed: {str(e)}", "code": "AI_ERROR"},
            )

        # 4. Update mastery exactly: mastery = 0.6 * old_mastery + 0.4 * score
        new_mastery = update_mastery_on_teachback(old_mastery, result.score)
        new_conf = update_confidence(old_conf, step=0.25)
        new_status = calculate_status(new_mastery, has_activity=True)

        # 5. Generate flashcards for missing points
        try:
            flashcards = ai_engine.make_flashcards(
                topic=topic,
                gap_type=gap_type,
                missing=result.missing,
                n=2,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": f"Flashcard generation failed: {str(e)}", "code": "AI_ERROR"},
            )

        # 6. Generate AI study note
        try:
            note_body = ai_engine.make_note(
                topic=topic,
                summary=result.feedback,
                lang=student["lang"],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": f"Note generation failed: {str(e)}", "code": "AI_ERROR"},
            )

        # 7. Persist teachback, flashcards, AI note, and updated topic state
        now_iso = datetime.now(timezone.utc).isoformat()
        today_str = clock.today(conn)

        tb_id = f"tb_{uuid.uuid4().hex[:12]}"
        conn.execute(
            """
            INSERT INTO teachbacks (
                id, student_id, topic_id, transcript, score,
                covered_json, missing_json, errors_json, feedback, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tb_id,
                req.student_id,
                req.topic_id,
                req.transcript.strip(),
                result.score,
                dumps_json(result.covered),
                dumps_json(result.missing),
                dumps_json(result.errors),
                result.feedback,
                now_iso,
            ),
        )

        # Persist flashcards with student ownership, due today
        persisted_cards: list[Flashcard] = []
        for card in flashcards:
            conn.execute(
                """
                INSERT INTO flashcards (
                    id, student_id, topic_id, front, back, source,
                    interval_days, ease, next_review, repetitions, created_at
                )
                VALUES (?, ?, ?, ?, ?, 'teachback', 0, 2.5, ?, 0, ?)
                """,
                (
                    card.id,
                    req.student_id,
                    req.topic_id,
                    card.front,
                    card.back,
                    today_str,
                    now_iso,
                ),
            )
            persisted_cards.append(card)

        # Persist AI note
        note_id = f"note_{uuid.uuid4().hex[:12]}"
        conn.execute(
            """
            INSERT INTO notes (id, student_id, topic_id, author, body, created_at)
            VALUES (?, ?, ?, 'ai', ?, ?)
            """,
            (note_id, req.student_id, req.topic_id, note_body, now_iso),
        )
        persisted_note = Note(
            id=note_id,
            topic_id=req.topic_id,
            author="ai",
            body=note_body,
            created_at=now_iso,
        )

        # Update topic state
        conn.execute(
            """
            INSERT INTO topic_state (
                student_id, topic_id, mastery, confidence, gap_type,
                interval_days, ease, next_review, status, repetitions, attempts_count
            )
            VALUES (?, ?, ?, ?, ?, 0, 2.5, ?, ?, 0, 1)
            ON CONFLICT(student_id, topic_id) DO UPDATE SET
                mastery = ?,
                confidence = ?,
                status = ?,
                next_review = COALESCE(topic_state.next_review, ?),
                attempts_count = topic_state.attempts_count + 1
            """,
            (
                req.student_id,
                req.topic_id,
                new_mastery,
                new_conf,
                gap_type,
                today_str,
                new_status,
                new_mastery,
                new_conf,
                new_status,
                today_str,
            ),
        )

        # Activity recording
        record_activity(conn, req.student_id, today_str)

        # Load fresh state
        final_state_row = conn.execute(
            "SELECT * FROM topic_state WHERE student_id = ? AND topic_id = ?",
            (req.student_id, req.topic_id),
        ).fetchone()

        updated_state = TopicState(
            topic_id=final_state_row["topic_id"],
            mastery=final_state_row["mastery"],
            confidence=final_state_row["confidence"],
            gap_type=final_state_row["gap_type"],
            interval_days=final_state_row["interval_days"],
            ease=final_state_row["ease"],
            next_review=final_state_row["next_review"],
            status=final_state_row["status"],
        )

    return TeachBackResponse(
        result=result,
        flashcards=persisted_cards,
        note=persisted_note,
        state=updated_state,
    )
