from fastapi import APIRouter, HTTPException, status
from backend.contracts import (
    DueFlashcardsResponse,
    FlashcardReviewRequest,
    FlashcardReviewResponse,
    Flashcard,
    TopicState,
)
from backend.db import get_db, record_activity
from backend.engine import clock
from backend.engine.srs import calculate_sm2

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("/due/{student_id}", response_model=DueFlashcardsResponse)
def get_due_flashcards(student_id: str):
    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        today_str = clock.today(conn)
        rows = conn.execute(
            """
            SELECT id, topic_id, front, back, source, next_review
            FROM flashcards
            WHERE student_id = ?
              AND (next_review IS NULL OR next_review <= ?)
            ORDER BY next_review ASC, created_at ASC
            """,
            (student_id, today_str),
        ).fetchall()

        cards: list[Flashcard] = [
            Flashcard(
                id=r["id"],
                topic_id=r["topic_id"],
                front=r["front"],
                back=r["back"],
                source=r["source"],
            )
            for r in rows
        ]

    return DueFlashcardsResponse(cards=cards)


@router.post("/review", response_model=FlashcardReviewResponse)
def review_flashcard(req: FlashcardReviewRequest):
    if req.quality < 0 or req.quality > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Quality must be between 0 and 5", "code": "INVALID_QUALITY"},
        )

    with get_db() as conn:
        card = conn.execute(
            "SELECT * FROM flashcards WHERE id = ? AND student_id = ?",
            (req.card_id, req.student_id),
        ).fetchone()

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Card not found or access denied", "code": "CARD_NOT_FOUND"},
            )

        today_str = clock.today(conn)

        # Apply SM-2 algorithm
        srs_result = calculate_sm2(
            quality=req.quality,
            current_interval=card["interval_days"],
            current_ease=card["ease"],
            repetitions=card["repetitions"],
            today_str=today_str,
        )

        # Update card
        conn.execute(
            """
            UPDATE flashcards
            SET interval_days = ?,
                ease = ?,
                next_review = ?,
                repetitions = ?
            WHERE id = ?
            """,
            (
                srs_result.interval_days,
                srs_result.ease,
                srs_result.next_review,
                srs_result.repetitions,
                req.card_id,
            ),
        )

        # Update topic_state for this topic and student
        topic_id = card["topic_id"]
        conn.execute(
            """
            UPDATE topic_state
            SET interval_days = ?,
                ease = ?,
                next_review = ?,
                repetitions = ?
            WHERE student_id = ? AND topic_id = ?
            """,
            (
                srs_result.interval_days,
                srs_result.ease,
                srs_result.next_review,
                srs_result.repetitions,
                req.student_id,
                topic_id,
            ),
        )

        record_activity(conn, req.student_id, today_str)

        # Fetch updated topic state
        state_row = conn.execute(
            "SELECT * FROM topic_state WHERE student_id = ? AND topic_id = ?",
            (req.student_id, topic_id),
        ).fetchone()

        if not state_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic state for '{topic_id}' not found", "code": "TOPIC_STATE_NOT_FOUND"},
            )

        updated_state = TopicState(
            topic_id=state_row["topic_id"],
            mastery=state_row["mastery"],
            confidence=state_row["confidence"],
            gap_type=state_row["gap_type"],
            interval_days=state_row["interval_days"],
            ease=state_row["ease"],
            next_review=state_row["next_review"],
            status=state_row["status"],
        )

    return FlashcardReviewResponse(state=updated_state)
