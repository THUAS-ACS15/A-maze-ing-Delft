"""Repository layer over the SQLite ``db`` module.

The schema is created at startup by ``db.init()`` (called from
``main.py``); these functions assume it already exists. Database errors
(e.g. ``IntegrityError``) propagate to the caller.
"""

from typing import Any

from db import connection


def create_user(name: str) -> int | None:
    with connection() as conn:
        cur = conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        return cur.lastrowid

def get_users() -> Any:
    with connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users"
            )
        row = cur.fetchall()
        if not row:
            return None
        return row

def get_user(name_or_id: str) -> Any:
    with connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE id = ? OR name = ?", (name_or_id, name_or_id)
            )
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)

def create_save(slot: str, user_id: int) -> int | None:
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO saves (slot, user_id) VALUES (?, ?)", (slot, user_id)
        )
        return cur.lastrowid


def get_user_saves(user_id: int) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM saves WHERE user_id = ?", (user_id,)
        ).fetchall()
    return [dict(row) for row in rows]

def get_user_save(user_id: int, slot: str) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM saves WHERE user_id = ? AND slot = ?",
            (user_id, slot),
        ).fetchone()
    return dict(row) if row else None

def create_scoreboard_entry(
    user_id: int,
    score: int,
    avg_room_time: str,
    exploration_time: str,
    assembly_time: str,
) -> int | None:
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO scoreboard "
            "(user_id, score, avg_room_time, exploration_time, assembly_time) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, score, avg_room_time, exploration_time, assembly_time),
        )
        return cur.lastrowid


def get_scoreboard_entries() -> list[dict[str, Any]]:
    """Return scoreboard rows ordered by highest score first."""
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM scoreboard ORDER BY score DESC, id ASC"
        ).fetchall()
    return [dict(row) for row in rows]
