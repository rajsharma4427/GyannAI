from datetime import date, timedelta
from typing import Optional
import sqlite3
from backend.db import get_db


def get_demo_day_offset(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("SELECT value FROM meta WHERE key = 'demo_day_offset'")
    row = cur.fetchone()
    if row and row["value"]:
        try:
            return int(row["value"])
        except ValueError:
            return 0
    return 0


def get_today_date(conn: Optional[sqlite3.Connection] = None) -> date:
    if conn is not None:
        offset = get_demo_day_offset(conn)
        return date.today() + timedelta(days=offset)
    with get_db() as c:
        offset = get_demo_day_offset(c)
        return date.today() + timedelta(days=offset)


def today(conn: Optional[sqlite3.Connection] = None) -> str:
    """Return the demo-aware current date as ISO string YYYY-MM-DD."""
    return get_today_date(conn).isoformat()


def advance_days(days: int, conn: Optional[sqlite3.Connection] = None) -> str:
    """Advance the demo clock by a given number of days. Days must be positive."""
    if not isinstance(days, int) or days <= 0:
        raise ValueError("Days to advance must be a positive integer.")

    def _do_advance(c: sqlite3.Connection) -> str:
        current_offset = get_demo_day_offset(c)
        new_offset = current_offset + days
        c.execute(
            """
            INSERT INTO meta (key, value) VALUES ('demo_day_offset', ?)
            ON CONFLICT(key) DO UPDATE SET value = ?
            """,
            (str(new_offset), str(new_offset)),
        )
        new_d = date.today() + timedelta(days=new_offset)
        return new_d.isoformat()

    if conn is not None:
        return _do_advance(conn)
    with get_db() as c:
        return _do_advance(c)
