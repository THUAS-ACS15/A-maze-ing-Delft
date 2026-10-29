"""Tests for the SQLite save database schema."""

import sqlite3

from utilities.save_management import recreate_db_table


def test_recreate_db_table_creates_all_tables():
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
