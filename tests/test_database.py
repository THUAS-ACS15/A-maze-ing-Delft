"""Tests for the root-level ``database`` module."""

import sqlite3

import pytest

import database


def _table_names(conn):
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }


def test_init_creates_all_tables(tmp_path):
    db = tmp_path / "game.db"

    database.init(db)

    assert db.exists()
    with database.connection(db) as conn:
        assert {"users", "saves", "scoreboard"} <= _table_names(conn)


def test_init_is_idempotent(tmp_path):
    db = tmp_path / "game.db"

    database.init(db)
    database.init(db)

    with database.connection(db) as conn:
        assert {"users", "saves", "scoreboard"} <= _table_names(conn)


def test_default_path_uses_database_path(monkeypatch, tmp_path):
    db = tmp_path / "game.db"
    monkeypatch.setattr(database, "DATABASE_PATH", db)

    database.init()

    assert db.exists()


def test_connection_does_not_create_tables(tmp_path):
    db = tmp_path / "game.db"

    with database.connection(db):
        pass

    with database.connection(db) as conn:
        assert _table_names(conn) == set()


def test_connection_commits(tmp_path):
    db = tmp_path / "game.db"
    database.init(db)

    with database.connection(db) as conn:
        conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))

    with database.connection(db) as conn:
        rows = conn.execute("SELECT name FROM users").fetchall()

    assert [row["name"] for row in rows] == ["Alice"]


def test_connection_rolls_back_on_error(tmp_path):
    db = tmp_path / "game.db"
    database.init(db)

    with pytest.raises(RuntimeError, match="boom"):
        with database.connection(db) as conn:
            conn.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
            raise RuntimeError("boom")

    with database.connection(db) as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]

    assert count == 0


def test_foreign_keys_are_enforced(tmp_path):
    db = tmp_path / "game.db"
    database.init(db)

    with pytest.raises(sqlite3.IntegrityError):
        with database.connection(db) as conn:
            conn.execute(
                "INSERT INTO saves (slot, user_id) VALUES (?, ?)",
                ("slot1", 999),
            )
