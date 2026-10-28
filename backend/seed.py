import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import sqlite3

from backend.contracts import Topic, Question, Lang
from backend.db import get_db, dumps_json
from backend.engine.backtrace import validate_topic_graph


def get_content_dir() -> Path:
    custom_dir = os.environ.get("CONTENT_DIR")
    if custom_dir:
        return Path(custom_dir)
    return Path(__file__).resolve().parent.parent / "content"


def load_and_seed_content(conn: sqlite3.Connection, content_dir: Optional[Path] = None) -> dict:
    """Load canonical content files and seed database idempotently."""
    c_dir = content_dir or get_content_dir()
    syllabus_path = c_dir / "syllabus_class10_math.json"
    questions_path = c_dir / "questions_seed.json"
    students_path = c_dir / "demo_students.json"

    missing_files = [str(p) for p in (syllabus_path, questions_path, students_path) if not p.exists()]
    if missing_files:
        raise FileNotFoundError(
            f"Seed files missing in '{c_dir}': {', '.join(missing_files)}. "
            "Please check CONTENT_DIR configuration or ensure content/ directory is present."
        )

    # 1. Load and validate syllabus
    with open(syllabus_path, "r", encoding="utf-8") as f:
        syllabus_raw = json.load(f)
    topics = [Topic(**item) for item in syllabus_raw]
    validate_topic_graph(topics)

    # Upsert topics and prerequisites
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

    # 2. Load and validate questions
    with open(questions_path, "r", encoding="utf-8") as f:
        questions_raw = json.load(f)
    questions = [Question(**item) for item in questions_raw]

    known_topic_ids = {t.id for t in topics}
    for q in questions:
        if q.topic_id not in known_topic_ids:
            raise ValueError(f"Question '{q.id}' references unknown topic '{q.topic_id}'")
        if len(q.options) != 4:
            raise ValueError(f"Question '{q.id}' must have exactly 4 options")
        if q.correct_index < 0 or q.correct_index >= 4:
            raise ValueError(f"Question '{q.id}' correct_index must be in [0, 3]")

        conn.execute(
            """
            INSERT INTO questions (id, topic_id, stem, options_json, correct_index, difficulty, misconception_tags_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                topic_id = excluded.topic_id,
                stem = excluded.stem,
                options_json = excluded.options_json,
                correct_index = excluded.correct_index,
                difficulty = excluded.difficulty,
                misconception_tags_json = excluded.misconception_tags_json
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

    # 3. Load and seed demo students
    with open(students_path, "r", encoding="utf-8") as f:
        students_raw = json.load(f)

    now_iso = datetime.now(timezone.utc).isoformat()
    for s in students_raw:
        s_id = s.get("student_id") or s.get("id")
        conn.execute(
            """
            INSERT OR IGNORE INTO students (id, name, lang, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (s_id, s["name"], s.get("lang", "en"), now_iso),
        )
        # Initialize student topic state for all topics if not present
        starting_map = {st["topic_id"]: st for st in s.get("starting_states", [])}
        for t in topics:
            if t.id in starting_map:
                st = starting_map[t.id]
                conn.execute(
                    """
                    INSERT INTO topic_state (
                        student_id, topic_id, mastery, confidence, gap_type,
                        interval_days, ease, next_review, status, repetitions, attempts_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                    ON CONFLICT(student_id, topic_id) DO UPDATE SET
                        mastery = excluded.mastery,
                        confidence = excluded.confidence,
                        gap_type = excluded.gap_type,
                        status = excluded.status
                    """,
                    (
                        s_id,
                        t.id,
                        st.get("mastery", 0.0),
                        st.get("confidence", 0.0),
                        st.get("gap_type"),
                        st.get("interval_days", 0),
                        st.get("ease", 2.5),
                        st.get("next_review"),
                        st.get("status", "gap" if st.get("gap_type") else "unseen"),
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO topic_state (
                        student_id, topic_id, mastery, confidence, gap_type,
                        interval_days, ease, next_review, status, repetitions, attempts_count
                    )
                    VALUES (?, ?, 0.0, 0.0, NULL, 0, 2.5, NULL, 'unseen', 0, 0)
                    """,
                    (s_id, t.id),
                )

    return {
        "topics_count": len(topics),
        "questions_count": len(questions),
        "students_count": len(students_raw),
    }


def seed_database(db_path: Optional[str] = None) -> dict:
    with get_db(db_path) as conn:
        return load_and_seed_content(conn)
