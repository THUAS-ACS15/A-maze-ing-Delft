"""Repository layer over the SQLite ``db`` module.

The schema is created at startup by ``db.init()`` (called from ``config.py``); these functions assume it already
exists. Each call opens its own short-lived connection and commits on success. Database errors (e.g.
``IntegrityError`` for a duplicate user name or save slot) propagate to the caller.
"""

from typing import Any

from db import connection

from .utils.parse_time import parse_time_str


def create_user(name: str) -> int | None:
    """Insert a new user.

    Args:
        name: Unique user name.

    Returns:
        The new user's row id.

    Raises:
        sqlite3.IntegrityError: If ``name`` is already taken.
    """
    with connection() as conn:
        cur = conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        return cur.lastrowid

def get_users() -> Any:
    """Fetch all users.

    Returns:
        A list of :class:`sqlite3.Row` objects, or ``None`` (not an empty list) when there are no users.
    """
    with connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users"
            )
        row = cur.fetchall()
        if not row:
            return None
        return row

def get_user(name_or_id: str) -> Any:
    """Look a user up by numeric id or by name.

    Args:
        name_or_id: User id or user name; both columns are matched.

    Returns:
        The user row as a ``dict``, or ``None`` if no user matches.
    """
    with connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE id = ? OR name = ?", (name_or_id, name_or_id)
            )
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)

def create_save(slot: str, user_id: int) -> int | None:
    """Record that ``user_id`` owns the save file ``slot``.

    Args:
        slot: Unique save slot name (the file stem under ``data/saves``).
        user_id: Owning user's id.

    Returns:
        The new row id.

    Raises:
        sqlite3.IntegrityError: If the slot already exists or ``user_id`` is unknown.
    """
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO saves (slot, user_id) VALUES (?, ?)", (slot, user_id)
        )
        return cur.lastrowid


def get_user_saves(user_id: int) -> list[dict[str, Any]]:
    """List a user's saves.

    Args:
        user_id: Owning user's id.

    Returns:
        Save rows as dicts (possibly empty), in insertion order.
    """
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM saves WHERE user_id = ?", (user_id,)
        ).fetchall()
    return [dict(row) for row in rows]

def get_user_save(user_id: int, slot: str) -> dict[str, Any] | None:
    """Find one save owned by a user.

    Args:
        user_id: Owning user's id.
        slot: Save slot name.

    Returns:
        The save row as a ``dict``, or ``None`` if the user does not own that slot.
    """
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
    """Insert a scoreboard row.

    Args:
        user_id: Id of the player who finished the game.
        score: Final score (see :func:`src.utils.score.calculate_score`).
        avg_room_time: Average time per room as an ``H:MM:SS`` string.
        exploration_time: Exploration-phase duration as an ``H:MM:SS`` string.
        assembly_time: Assembly-phase duration as an ``H:MM:SS`` string.

    Returns:
        The new row id.
    """
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO scoreboard "
            "(user_id, score, avg_room_time, exploration_time, assembly_time) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, score, avg_room_time, exploration_time, assembly_time),
        )
        return cur.lastrowid


def _total_time_seconds(entry: dict[str, Any]) -> float:
    """Return exploration plus assembly time of a scoreboard row in seconds.

    Args:
        entry: Scoreboard row as a dict.
    """
    return (
        parse_time_str(entry["exploration_time"]).total_seconds()
        + parse_time_str(entry["assembly_time"]).total_seconds()
    )


def get_scoreboard_entries() -> list[dict[str, Any]]:
    """Return scoreboard rows: highest score first, then fastest total time."""
    with connection() as conn:
        rows = conn.execute("SELECT * FROM scoreboard").fetchall()
    entries = [dict(row) for row in rows]
    # Times are stored as text, so tie-break on parsed seconds; id keeps the order deterministic.
    entries.sort(
        key=lambda entry: (-entry["score"], _total_time_seconds(entry), entry["id"])
    )
    return entries
