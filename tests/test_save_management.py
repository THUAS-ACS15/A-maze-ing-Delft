"""Tests for the SQLite save database schema and persistence behavior."""

import sqlite3

from utilities.save_management import (
    get_save_info,
    load_save,
    recreate_db_table,
    save_game,
)


def test_recreate_db_table_creates_all_tables():
    """Create every table required by the save database schema."""
    db = sqlite3.connect(":memory:")
    try:
        recreate_db_table(db)
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
    finally:
        db.close()

    assert tables == {
        "general",
        "inventory",
        "room_completed_status",
        "room_visited_status",
        "store_items",
    }


def test_save_and_load_round_trip(monkeypatch, tmp_path):
    """Persist the gameplay state and reconstruct it from the selected slot."""
    monkeypatch.chdir(tmp_path)
    state = {
        "player_name": "Ada",
        "current_room": "teachersroom1",
        "previous_room": "eastcorridor",
        "time_elapsed": 125.5,
        "start_time": 999.0,
        "is_gametime_paused": True,
        "has_intro_played": True,
        "current_objective_id": 3,
        "student_id_obtained": True,
        "visited": {"frontdesk": True, "teachersroom1": True},
        "completed": {"frontdesk": True, "teachersroom1": False},
        "inventory": ["Student ID card", "Staff Keycard"],
    }

    save_game(state, 2)

    assert get_save_info(1) is None
    assert get_save_info(2) == {
        "save_slot": 2,
        "player_name": "Ada",
        "current_room": "teachersroom1",
        "previous_room": "eastcorridor",
        "time_elapsed": 125.5,
        "visited_percent": 100.0,
        "completion_percent": 50.0,
    }

    loaded = load_save(2)

    assert loaded is not None
    assert loaded["player_name"] == "Ada"
    assert loaded["current_room"] == "teachersroom1"
    assert loaded["previous_room"] == "eastcorridor"
    assert loaded["time_elapsed"] == 125.5
    assert loaded["has_intro_played"] is True
    assert loaded["current_objective_id"] == 3
    assert loaded["student_id_obtained"] is True
    assert loaded["visited"] == state["visited"]
    assert loaded["completed"] == state["completed"]
    assert loaded["inventory"] == sorted(state["inventory"])
    assert loaded["is_gametime_paused"] is False
    assert isinstance(loaded["start_time"], float)
