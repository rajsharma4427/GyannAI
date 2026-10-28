import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional


DEFAULT_DB_PATH = os.environ.get("DB_PATH") or str(
    Path(__file__).resolve().parent / "gyaan_loop.db"
)


def get_db_path() -> str:
    return os.environ.get("DB_PATH", DEFAULT_DB_PATH)


@contextmanager
def get_db(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    target_path = db_path or get_db_path()
    # Ensure directory exists
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)

    with get_db(target_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                lang TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                parent_id TEXT,
                description TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS topic_prereqs (
                topic_id TEXT NOT NULL,
                prereq_id TEXT NOT NULL,
                PRIMARY KEY (topic_id, prereq_id),
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
                FOREIGN KEY (prereq_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS topic_state (
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                mastery REAL NOT NULL DEFAULT 0.0,
                confidence REAL NOT NULL DEFAULT 0.0,
                gap_type TEXT,
                interval_days INTEGER NOT NULL DEFAULT 0,
                ease REAL NOT NULL DEFAULT 2.5,
                next_review TEXT,
                status TEXT NOT NULL DEFAULT 'unseen',
                repetitions INTEGER NOT NULL DEFAULT 0,
                attempts_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (student_id, topic_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL,
                stem TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_index INTEGER NOT NULL,
                difficulty INTEGER NOT NULL,
                misconception_tags_json TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS diagnostic_sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                current_difficulty INTEGER NOT NULL DEFAULT 2,
                questions_answered INTEGER NOT NULL DEFAULT 0,
                current_topic_id TEXT NOT NULL,
                visited_topics_json TEXT NOT NULL DEFAULT '[]',
                root_gaps_json TEXT NOT NULL DEFAULT '[]',
                current_question_id TEXT,
                backtrace_history_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                chosen_index INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                time_ms INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES diagnostic_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS flashcards (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                source TEXT NOT NULL,
                interval_days INTEGER NOT NULL DEFAULT 0,
                ease REAL NOT NULL DEFAULT 2.5,
                next_review TEXT,
                repetitions INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                author TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS teachbacks (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                transcript TEXT NOT NULL,
                score REAL NOT NULL,
                covered_json TEXT NOT NULL,
                missing_json TEXT NOT NULL,
                errors_json TEXT NOT NULL,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS daily_activity (
                student_id TEXT NOT NULL,
                activity_date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (student_id, activity_date),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_questions_topic_diff ON questions (topic_id, difficulty);
            CREATE INDEX IF NOT EXISTS idx_flashcards_student_due ON flashcards (student_id, next_review);
            CREATE INDEX IF NOT EXISTS idx_notes_student_topic ON notes (student_id, topic_id);
            CREATE INDEX IF NOT EXISTS idx_attempts_session ON attempts (session_id);
            CREATE INDEX IF NOT EXISTS idx_topic_state_student ON topic_state (student_id);
            CREATE INDEX IF NOT EXISTS idx_daily_activity_student ON daily_activity (student_id, activity_date);
            """
        )


def record_activity(conn: sqlite3.Connection, student_id: str, activity_date: str) -> None:
    conn.execute(
        """
        INSERT INTO daily_activity (student_id, activity_date, count)
        VALUES (?, ?, 1)
        ON CONFLICT(student_id, activity_date) DO UPDATE SET count = count + 1
        """,
        (student_id, activity_date),
    )


def dumps_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def loads_json(text: Optional[str], default: Any = None) -> Any:
    if not text:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default
