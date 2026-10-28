from datetime import timedelta
from fastapi import APIRouter, HTTPException, status

from backend.contracts import DashboardResponse, WeakestTopic
from backend.db import get_db
from backend.engine import clock

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _calculate_streak(conn, student_id: str) -> int:
    current_date = clock.get_today_date(conn)
    rows = conn.execute(
        "SELECT activity_date FROM daily_activity WHERE student_id = ? ORDER BY activity_date DESC",
        (student_id,),
    ).fetchall()

    if not rows:
        return 0

    active_dates = {r["activity_date"] for r in rows}

    # If student has activity today, start counting from today.
    # If not, check if student had activity yesterday (streak still alive for today).
    if current_date.isoformat() in active_dates:
        check_date = current_date
    elif (current_date - timedelta(days=1)).isoformat() in active_dates:
        check_date = current_date - timedelta(days=1)
    else:
        return 0

    streak = 0
    while check_date.isoformat() in active_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


@router.get("/{student_id}", response_model=DashboardResponse)
def get_dashboard(student_id: str):
    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        # Get all topic states for this student
        state_rows = conn.execute(
            """
            SELECT topic_id, mastery, status
            FROM topic_state
            WHERE student_id = ?
            ORDER BY mastery ASC
            """,
            (student_id,),
        ).fetchall()

        topics_total = len(state_rows)
        if topics_total == 0:
            overall_mastery = 0.0
            topics_mastered = 0
            weakest = []
        else:
            total_mastery = sum(r["mastery"] for r in state_rows)
            overall_mastery = round(total_mastery / topics_total, 4)
            topics_mastered = sum(1 for r in state_rows if r["status"] == "mastered" or r["mastery"] > 0.8)
            # Weakest topics: up to 5 topics in ascending mastery order
            weakest = [
                WeakestTopic(topic_id=r["topic_id"], mastery=round(r["mastery"], 4))
                for r in state_rows[:5]
            ]

        # Due flashcards today
        today_str = clock.today(conn)
        due_row = conn.execute(
            """
            SELECT COUNT(*) AS due_count
            FROM flashcards
            WHERE student_id = ?
              AND (next_review IS NULL OR next_review <= ?)
            """,
            (student_id, today_str),
        ).fetchone()
        due_today = due_row["due_count"] if due_row else 0

        # Streak calculation
        streak_days = _calculate_streak(conn, student_id)

    return DashboardResponse(
        overall_mastery=overall_mastery,
        topics_mastered=topics_mastered,
        topics_total=topics_total,
        due_today=due_today,
        streak_days=streak_days,
        weakest=weakest,
    )
