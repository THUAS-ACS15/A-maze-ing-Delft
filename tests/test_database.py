"""Tests for the root-level ``db`` module."""

import sqlite3
import pytest
import db


def _table_names(conn):
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }


def test_init_creates_all_tables(tmp_path):
    db_path = tmp_path / "game.db"

    db.init(db_path)

    assert db_path.exists()
    with db.connection(db_path) as conn:
        assert {"users", "saves", "scoreboard"} <= _table_names(conn)


def test_init_is_idempotent(tmp_path):
    db_path = tmp_path / "game.db"

    db.init(db_path)
    db.init(db_path)

    with db.connection(db_path) as conn:
        assert {"users", "saves", "scoreboard"} <= _table_names(conn)


def test_default_path_uses_database_path(monkeypatch, tmp_path):
    db_path = tmp_path / "game.db"
    monkeypatch.setattr(db, "DATABASE_PATH", db_path)

    db.init()

    assert db_path.exists()


def test_connection_does_not_create_tables(tmp_path):
    db_path = tmp_path / "game.db"

    with db.connection(db_path):
        pass

    with db.connection(db_path) as conn:
        assert _table_names(conn) == set()


def test_connection_commits(tmp_path):
    db_path = tmp_path / "game.db"
    db.init(db_path)

    with db.connection(db_path) as conn:
        conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))

    with db.connection(db_path) as conn:
        rows = conn.execute("SELECT name FROM users").fetchall()

    assert [row["name"] for row in rows] == ["Alice"]


def test_connection_rolls_back_on_error(tmp_path):
    db_path = tmp_path / "game.db"
    db.init(db_path)

    with pytest.raises(RuntimeError, match="boom"):
        with db.connection(db_path) as conn:
            conn.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
            raise RuntimeError("boom")

    with db.connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]

    assert count == 0


def test_foreign_keys_are_enforced(tmp_path):
    db_path = tmp_path / "game.db"
    db.init(db_path)

    with pytest.raises(sqlite3.IntegrityError):
        with db.connection(db_path) as conn:
            conn.execute(
                "INSERT INTO saves (slot, user_id) VALUES (?, ?)",
                ("slot1", 999),
            )
