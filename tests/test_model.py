"""Tests for ``src/model.py``."""

import sqlite3

import pytest

import db
from src import model


@pytest.fixture
def database(monkeypatch, tmp_path):
    """Point the db module at a throwaway database and create the schema."""
    db_path = tmp_path / "game.db"
    monkeypatch.setattr(db, "DATABASE_PATH", db_path)
    db.init()
    return db_path


def test_create_user_persists_row(database):
    user_id = model.create_user("Alice")

    assert isinstance(user_id, int)
    with db.connection() as conn:
        row = conn.execute(
            "SELECT name FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    assert row["name"] == "Alice"


def test_create_save_uses_saves_table(database):
    user_id = model.create_user("Alice")

    save_id = model.create_save("slot1", user_id)

    with db.connection() as conn:
        row = conn.execute(
            "SELECT slot, user_id FROM saves WHERE id = ?", (save_id,)
        ).fetchone()
        user_count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    assert row["slot"] == "slot1"
    assert row["user_id"] == user_id
    assert user_count == 1  # create_save did not insert a user


def test_get_user_saves_filters_by_user(database):
    alice = model.create_user("Alice")
    bob = model.create_user("Bob")
    model.create_save("alice-1", alice)
    model.create_save("alice-2", alice)
    model.create_save("bob-1", bob)

    saves = model.get_user_saves(alice)

    assert {save["slot"] for save in saves} == {"alice-1", "alice-2"}


def test_create_scoreboard_entry_persists_row(database):
    user_id = model.create_user("Alice")

    entry_id = model.create_scoreboard_entry(user_id, 100, "0:30", "1:00", "0:45")

    with db.connection() as conn:
        row = conn.execute(
            "SELECT * FROM scoreboard WHERE id = ?", (entry_id,)
        ).fetchone()
    assert row["user_id"] == user_id
    assert row["score"] == 100
    assert row["assembly_time"] == "0:45"


def test_get_scoreboard_entries_returns_rows(database):
    user_id = model.create_user("Alice")
    model.create_scoreboard_entry(user_id, 100, "0:30", "1:00", "0:45")

    entries = model.get_scoreboard_entries()

    assert len(entries) == 1
    assert entries[0]["score"] == 100
    assert entries[0]["exploration_time"] == "1:00"


def test_create_save_with_unknown_user_raises(database):
    with pytest.raises(sqlite3.IntegrityError):
        model.create_save("slot1", 999)


def test_get_user_by_name(database):
    user_id = model.create_user("Alice")

    user = model.get_user("Alice")

    assert user["id"] == user_id
    assert user["name"] == "Alice"


def test_get_user_by_id(database):
    user_id = model.create_user("Alice")

    user = model.get_user(user_id)

    assert user["id"] == user_id
    assert user["name"] == "Alice"


def test_get_user_missing_returns_none(database):
    assert model.get_user("Nobody") is None


def test_get_user_save_returns_owned_slot(database):
    alice = model.create_user("Alice")
    bob = model.create_user("Bob")
    model.create_save("alice-1", alice)

    save = model.get_user_save(alice, "alice-1")

    assert save["slot"] == "alice-1"
    assert save["user_id"] == alice
    assert model.get_user_save(bob, "alice-1") is None
    assert model.get_user_save(alice, "missing") is None


def test_get_users_returns_rows(database):
    model.create_user("Alice")
    model.create_user("Bob")

    users = model.get_users()

    assert {row["name"] for row in users} == {"Alice", "Bob"}


def test_get_users_empty_returns_none(database):
    assert model.get_users() is None
