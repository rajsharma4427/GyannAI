import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from backend.contracts import (
    DiagnosticStartRequest,
    DiagnosticStartResponse,
    DiagnosticAnswerRequest,
    DiagnosticAnswerResponse,
    Question,
    Topic,
    BacktraceInfo,
    DiagnosticSummary,
    GapItem,
)
from backend.db import get_db, dumps_json, loads_json, record_activity
from backend.engine import clock
from backend.engine.diagnostic import next_difficulty, MAX_DIAGNOSTIC_QUESTIONS
from backend.engine.backtrace import evaluate_backtrace_step
from backend.engine.mastery import (
    update_mastery_on_answer,
    update_confidence,
    calculate_status,
)
import ai_engine

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])


def _row_to_question(row) -> Question:
    return Question(
        id=row["id"],
        topic_id=row["topic_id"],
        stem=row["stem"],
        options=loads_json(row["options_json"], []),
        correct_index=row["correct_index"],
        difficulty=row["difficulty"],
        misconception_tags=loads_json(row["misconception_tags_json"], []),
    )


def _get_or_generate_question(
    conn,
    topic_id: str,
    difficulty: int,
    exclude_question_ids: list[str],
) -> Question:
    """Find an unanswered question from seed bank; if unavailable, generate via AI."""
    # Try exact difficulty first
    query = """
        SELECT * FROM questions
        WHERE topic_id = ? AND difficulty = ?
    """
    params = [topic_id, difficulty]
    if exclude_question_ids:
        placeholders = ",".join("?" for _ in exclude_question_ids)
        query += f" AND id NOT IN ({placeholders})"
        params.extend(exclude_question_ids)
    query += " ORDER BY rowid LIMIT 1"

    row = conn.execute(query, params).fetchone()
    if row:
        return _row_to_question(row)

    # Try any other difficulty for this topic
    alt_query = """
        SELECT * FROM questions
        WHERE topic_id = ?
    """
    alt_params = [topic_id]
    if exclude_question_ids:
        placeholders = ",".join("?" for _ in exclude_question_ids)
        alt_query += f" AND id NOT IN ({placeholders})"
        alt_params.extend(exclude_question_ids)
    alt_query += " ORDER BY ABS(difficulty - ?) LIMIT 1"
    alt_params.append(difficulty)

    row = conn.execute(alt_query, alt_params).fetchone()
    if row:
        return _row_to_question(row)

    # If seed bank is exhausted, generate with AI engine
    topic_row = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not topic_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"Topic '{topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
        )
    topic_obj = Topic(
        id=topic_row["id"],
        name=topic_row["name"],
        parent_id=topic_row["parent_id"],
        description=topic_row["description"] or "",
    )

    generated = ai_engine.generate_questions(topic_obj, 1, difficulty)
    if not generated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate question", "code": "AI_ERROR"},
        )
    q = generated[0]
    conn.execute(
        """
        INSERT INTO questions (id, topic_id, stem, options_json, correct_index, difficulty, misconception_tags_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        (
            q.id,
            q.topic_id,
            q.stem,
            dumps_json(q.options),
            q.correct_index,
            q.difficulty,
            dumps_json(q.misconception_tags),
        ),
    )
    return q


@router.post("/start", response_model=DiagnosticStartResponse)
def start_diagnostic(req: DiagnosticStartRequest):
    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (req.student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{req.student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        topic = conn.execute("SELECT id, name FROM topics WHERE id = ?", (req.topic_id,)).fetchone()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Topic '{req.topic_id}' not found", "code": "TOPIC_NOT_FOUND"},
            )

        session_id = f"diag_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        initial_difficulty = 2

        # Select initial question at difficulty 2
        question = _get_or_generate_question(conn, req.topic_id, initial_difficulty, [])

        conn.execute(
            """
            INSERT INTO diagnostic_sessions (
                id, student_id, topic_id, status, current_difficulty,
                questions_answered, current_topic_id, visited_topics_json,
                root_gaps_json, current_question_id, backtrace_history_json,
                created_at, updated_at
            )
            VALUES (?, ?, ?, 'active', ?, 0, ?, ?, '[]', ?, '[]', ?, ?)
            """,
            (
                session_id,
                req.student_id,
                req.topic_id,
                initial_difficulty,
                req.topic_id,
                dumps_json([req.topic_id]),
                question.id,
                now_iso,
                now_iso,
            ),
        )

    return DiagnosticStartResponse(session_id=session_id, question=question)


@router.post("/answer", response_model=DiagnosticAnswerResponse)
def answer_diagnostic(req: DiagnosticAnswerRequest):
    if req.chosen_index < 0 or req.chosen_index > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "chosen_index must be between 0 and 3", "code": "INVALID_INDEX"},
        )

    with get_db() as conn:
        session = conn.execute(
            "SELECT * FROM diagnostic_sessions WHERE id = ?",
            (req.session_id,),
        ).fetchone()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Session '{req.session_id}' not found", "code": "SESSION_NOT_FOUND"},
            )

        if session["status"] == "done":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Session is already completed", "code": "SESSION_ALREADY_COMPLETED"},
            )

        if session["current_question_id"] != req.question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Question ID does not match current session question",
                    "code": "INVALID_QUESTION",
                },
            )

        question_row = conn.execute(
            "SELECT * FROM questions WHERE id = ?",
            (req.question_id,),
        ).fetchone()
        if not question_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Question '{req.question_id}' not found", "code": "QUESTION_NOT_FOUND"},
            )

        question = _row_to_question(question_row)
        is_correct = (req.chosen_index == question.correct_index)

        student_id = session["student_id"]
        current_topic_id = session["current_topic_id"]
        visited_topics: list[str] = loads_json(session["visited_topics_json"], [])
        root_gaps: list[dict] = loads_json(session["root_gaps_json"], [])
        backtrace_history: list[dict] = loads_json(session["backtrace_history_json"], [])

        # Persist attempt
        attempt_id = f"att_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO attempts (id, session_id, student_id, topic_id, question_id, chosen_index, is_correct, time_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                req.session_id,
                student_id,
                current_topic_id,
                req.question_id,
                req.chosen_index,
                1 if is_correct else 0,
                req.time_ms,
                now_iso,
            ),
        )

        # Record daily activity
        today_str = clock.today(conn)
        record_activity(conn, student_id, today_str)

        # Get prerequisites for current topic
        prereq_rows = conn.execute(
            """
            SELECT t.id, t.name, t.parent_id, t.description
            FROM topics t
            JOIN topic_prereqs tp ON t.id = tp.prereq_id
            WHERE tp.topic_id = ?
            """,
            (current_topic_id,),
        ).fetchall()
        prereqs = [
            Topic(
                id=pr["id"],
                name=pr["name"],
                parent_id=pr["parent_id"],
                description=pr["description"] or "",
            )
            for pr in prereq_rows
        ]
        prereq_ids = [p.id for p in prereqs]

        # Fetch current topic model
        curr_topic_row = conn.execute("SELECT * FROM topics WHERE id = ?", (current_topic_id,)).fetchone()
        current_topic_model = Topic(
            id=curr_topic_row["id"],
            name=curr_topic_row["name"],
            parent_id=curr_topic_row["parent_id"],
            prereq_ids=prereq_ids,
            description=curr_topic_row["description"] or "",
        )

        # Evaluate answer with MistakeAnalysis / Backtrace if incorrect
        backtrace_info: Optional[BacktraceInfo] = None
        identified_gap: Optional[str] = None
        target_next_topic = current_topic_id

        if not is_correct:
            analysis = ai_engine.classify_mistake(
                question=question,
                chosen_index=req.chosen_index,
                topic=current_topic_model,
                prereqs=prereqs,
            )

            current_depth = len(backtrace_history)
            next_topic, bt_info, gap_recorded = evaluate_backtrace_step(
                analysis=analysis,
                current_topic_id=current_topic_id,
                allowed_prereq_ids=prereq_ids,
                visited_topics=visited_topics,
                current_depth=current_depth,
            )

            if next_topic:
                target_next_topic = next_topic
                backtrace_info = bt_info
                backtrace_history.append(
                    {
                        "from_topic_id": current_topic_id,
                        "to_topic_id": next_topic,
                        "reason": analysis.reason,
                    }
                )
                if next_topic not in visited_topics:
                    visited_topics.append(next_topic)
            else:
                identified_gap = gap_recorded or analysis.gap_type
                if not any(g.get("topic_id") == current_topic_id for g in root_gaps):
                    root_gaps.append({"topic_id": current_topic_id, "gap_type": identified_gap})

        # Update mastery and confidence for current topic
        state_row = conn.execute(
            "SELECT * FROM topic_state WHERE student_id = ? AND topic_id = ?",
            (student_id, current_topic_id),
        ).fetchone()

        old_mastery = state_row["mastery"] if state_row else 0.0
        old_conf = state_row["confidence"] if state_row else 0.0
        new_mastery = update_mastery_on_answer(
            current_mastery=old_mastery,
            is_correct=is_correct,
            gap_type=identified_gap,
        )
        new_conf = update_confidence(old_conf)
        new_status = calculate_status(new_mastery, has_activity=True)

        conn.execute(
            """
            INSERT INTO topic_state (
                student_id, topic_id, mastery, confidence, gap_type,
                interval_days, ease, next_review, status, repetitions, attempts_count
            )
            VALUES (?, ?, ?, ?, ?, 0, 2.5, NULL, ?, 0, 1)
            ON CONFLICT(student_id, topic_id) DO UPDATE SET
                mastery = ?,
                confidence = ?,
                gap_type = COALESCE(?, topic_state.gap_type),
                status = ?,
                attempts_count = topic_state.attempts_count + 1
            """,
            (
                student_id,
                current_topic_id,
                new_mastery,
                new_conf,
                identified_gap,
                new_status,
                new_mastery,
                new_conf,
                identified_gap,
                new_status,
            ),
        )

        # Adapt difficulty
        new_diff = next_difficulty(session["current_difficulty"], is_correct)
        questions_answered = session["questions_answered"] + 1

        # Check termination:
        # 1. 8 questions answered
        # 2. Or root gaps found and no further backtrace
        # 3. Or answered correctly on prerequisite topic
        is_done = False
        if questions_answered >= MAX_DIAGNOSTIC_QUESTIONS:
            is_done = True
        elif is_correct and current_topic_id != session["topic_id"] and len(root_gaps) >= 1:
            # Reached a solid prerequisite topic
            is_done = True
        elif not is_correct and len(root_gaps) >= 1 and backtrace_info is None:
            # Found root gap and cannot backtrace further
            is_done = True

        if is_done:
            conn.execute(
                """
                UPDATE diagnostic_sessions
                SET status = 'done',
                    questions_answered = ?,
                    current_difficulty = ?,
                    visited_topics_json = ?,
                    root_gaps_json = ?,
                    backtrace_history_json = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    questions_answered,
                    new_diff,
                    dumps_json(visited_topics),
                    dumps_json(root_gaps),
                    dumps_json(backtrace_history),
                    now_iso,
                    req.session_id,
                ),
            )

            summary_items = [
                GapItem(topic_id=g["topic_id"], gap_type=g["gap_type"])
                for g in root_gaps
            ]
            return DiagnosticAnswerResponse(
                correct=is_correct,
                done=True,
                next_question=None,
                backtrace=backtrace_info,
                summary=DiagnosticSummary(gaps=summary_items),
            )

        # Diagnostic continues: fetch next question
        used_q_rows = conn.execute(
            "SELECT question_id FROM attempts WHERE session_id = ?",
            (req.session_id,),
        ).fetchall()
        exclude_ids = [r["question_id"] for r in used_q_rows]

        next_q = _get_or_generate_question(
            conn=conn,
            topic_id=target_next_topic,
            difficulty=new_diff,
            exclude_question_ids=exclude_ids,
        )

        conn.execute(
            """
            UPDATE diagnostic_sessions
            SET questions_answered = ?,
                current_difficulty = ?,
                current_topic_id = ?,
                current_question_id = ?,
                visited_topics_json = ?,
                root_gaps_json = ?,
                backtrace_history_json = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                questions_answered,
                new_diff,
                target_next_topic,
                next_q.id,
                dumps_json(visited_topics),
                dumps_json(root_gaps),
                dumps_json(backtrace_history),
                now_iso,
                req.session_id,
            ),
        )

        return DiagnosticAnswerResponse(
            correct=is_correct,
            done=False,
            next_question=next_q,
            backtrace=backtrace_info,
            summary=None,
        )
