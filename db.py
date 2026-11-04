"""SQLite persistence for users, saves, and the scoreboard.

The database lives at ``data/game.db`` and is created lazily on first connect. Foreign keys are enforced and rows
are returned as :class:`sqlite3.Row`. Higher-level queries live in :mod:`src.model`.

Attributes:
    DATABASE_PATH: Default location of the SQLite database file.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

_BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = _BASE_DIR / "data" / "game.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS saves (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    slot       TEXT NOT NULL UNIQUE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS scoreboard (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score            INTEGER NOT NULL,
    avg_room_time    TEXT NOT NULL,
    exploration_time TEXT NOT NULL,
    assembly_time    TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection with FK enforcement and ``sqlite3.Row`` access.

    Args:
        db_path: Database file to open. Defaults to :data:`DATABASE_PATH`. Parent directories are created if missing.

    Returns:
        An open connection. The caller is responsible for closing it; prefer :func:`connection`.
    """
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a connection that commits on success and always closes.

    Args:
        db_path: Database file to open. Defaults to :data:`DATABASE_PATH`.

    Yields:
        An open connection. The transaction is committed when the block exits normally and rolled back if it raises.

    Raises:
        Exception: Any exception raised inside the ``with`` block is re-raised after the rollback.
    """
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init(db_path: Path | None = None) -> None:
    """Create the tables idempotently.

    Args:
        db_path: Database file to initialise. Defaults to :data:`DATABASE_PATH`.
    """
    with connection(db_path) as conn:
        conn.executescript(_SCHEMA)

