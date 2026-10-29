# -----------------------------------------------------------------------------
# File: save_management.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

import sqlite3
import time

DB_TABLE_STRUCTURE = """  
CREATE TABLE IF NOT EXISTS general (
    save_slot INTEGER PRIMARY KEY,
    current_room TEXT NOT NULL,
    previous_room TEXT,
    time_elapsed REAL NOT NULL,
    has_intro_played INTEGER NOT NULL,
    current_objective_id INTEGER NOT NULL,
    student_id_obtained INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS room_visited_status (
    save_slot INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    is_visited INTEGER NOT NULL,
    PRIMARY KEY (save_slot, room_name)
);

CREATE TABLE IF NOT EXISTS room_completed_status (
    save_slot INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    is_complete INTEGER NOT NULL,
    PRIMARY KEY (save_slot, room_name)
);

CREATE TABLE IF NOT EXISTS inventory (
    save_slot INTEGER NOT NULL,
    item TEXT NOT NULL,
    PRIMARY KEY (save_slot, item)
);

CREATE TABLE IF NOT EXISTS store_items (
    save_slot INTEGER NOT NULL,
    item TEXT NOT NULL,
    PRIMARY KEY (save_slot, item)
);
"""

def update_elapsed_time(state: dict) -> None:
    """Add the current active session duration to the saved elapsed time."""
    if state.get("is_gametime_paused"):
        return

    start_time = state.get("start_time")
    if not isinstance(start_time, (int, float)) or isinstance(start_time, bool):
        return

    elapsed_since_start = time.time() - start_time
    state["time_elapsed"] = state.get("time_elapsed", 0.0) + elapsed_since_start
    state["start_time"] = time.time()


def recreate_db_table(db: sqlite3.Connection) -> None:
    """
    Recreates the database 'saves' table.
    
    This function ensures that the database table structure is up-to-date,
    by executing the SQL script defined in DB_TABLE_STRUCTURE.
    
    Inputs:
        - db: An active SQLite database connection.
        
    Outputs: NONE
    """
    cursor = db.cursor()
    cursor.executescript(DB_TABLE_STRUCTURE)
    db.commit()

def get_save_info(slot: int) -> dict | None:
    """
    Retrieves some save info from the specified slot, for display in the save GUI.

    This function retrieves the current room, coin balance, exploration percentage,
    and time elapsed from the specified save slot in the database.

    Inputs:
        - slot: The save slot number (1, 2, or 3).
    
    Outputs:
        - A dict containing current room, exploration % and time played.
    """

    with sqlite3.connect("saves.db", timeout = 5.0) as save_db:
        recreate_db_table(save_db)
        cursor = save_db.cursor()

        cursor.execute(
            "SELECT current_room, previous_room, time_elapsed "
            "FROM general WHERE save_slot = ?",
            (slot,),
        )

        info = cursor.fetchone()

        # Guard against no save data in slot
        if info is None:
            return None
        
        # Get visited rooms
        cursor.execute(
            "SELECT room_name, is_visited FROM room_visited_status "
            "WHERE save_slot = ?",
            (slot,),
        )

        room_visited_data = cursor.fetchall()

        # Get completed rooms
        cursor.execute(
            "SELECT room_name, is_complete FROM room_completed_status "
            "WHERE save_slot = ?",
            (slot,),
        )

        room_completion_data = cursor.fetchall()

        # Get completed %
        completed_count = 0
        for _, is_completed in room_completion_data:
            if is_completed:
                completed_count += 1

        # Get visited %
        visited_count = 0
        for _, is_visited in room_visited_data:
            if is_visited:
                visited_count += 1

        visited_percent = (
            (visited_count / len(room_visited_data)) * 100
            if room_visited_data
            else 0
        )

        completion_percent = (
            (completed_count / len(room_completion_data)) * 100
            if room_completion_data
            else 0
        )
        
        return {
            "save_slot": slot,
            "current_room": info[0],
            "previous_room": info[1],
            "time_elapsed": info[2],
            "visited_percent": round(visited_percent, 2),
            "completion_percent": round(completion_percent, 2)
        }

def save_game(state: dict, slot: int) -> None:
    """
    Save the game state to the specified slot.

    Inputs:
        - slot: The save slot number (1, 2, or 3).
        - state: The current game state dictionary.
    
    Outputs: NONE
    """
    if not isinstance(state, dict):
        raise TypeError(
            "state must be a dictionary containing the game state, "
            f"not {type(state).__name__}"
    )

    update_elapsed_time(state)

    with sqlite3.connect("saves.db", timeout = 5.0) as save_db:
        recreate_db_table(save_db)
        cursor = save_db.cursor()

        # Save the general game state
        cursor.execute("""
            INSERT OR REPLACE INTO general 
            (save_slot, current_room, previous_room, time_elapsed, has_intro_played,
            current_objective_id, student_id_obtained)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slot,
                state["current_room"],
                state["previous_room"],
                state["time_elapsed"],
                int(state["has_intro_played"]),
                state["current_objective_id"],
                int(state["student_id_obtained"]),
            ),
        )

        # Save room visited status
        for room_name, is_visited in state["visited"].items():
            cursor.execute("""
                INSERT OR REPLACE INTO room_visited_status 
                (save_slot, room_name, is_visited)
                VALUES (?, ?, ?)
                """,
                (slot, room_name, int(is_visited)),
        )
            
        # Save room completion status
        for room_name, is_complete in state["completed"].items():
            cursor.execute("""
                INSERT OR REPLACE INTO room_completed_status 
                (save_slot, room_name, is_complete)
                VALUES (?, ?, ?)
                """,
                (slot, room_name, int(is_complete)),
        )

        # Save inventory
        for item in state["inventory"]:
            cursor.execute("""
                INSERT OR REPLACE INTO inventory 
                (save_slot, item)
                VALUES (?, ?)
                """,
                (slot, item),
        )

        save_db.commit()

def load_save(slot: int) -> dict | None:
    """
    Load the save data from the specified slot.

    Returns a dictionary with the save data, or None if no save is found.

    Inputs:
        - slot: The save slot number (1, 2, or 3).

    Outputs:
        state (dict): the state dict from the last save.
    """

    with sqlite3.connect("saves.db", timeout = 5.0) as save_db:
        recreate_db_table(save_db)
        cursor = save_db.cursor()
        reconstructed_state = {}

        # Get general state data
        cursor.execute(
            "SELECT current_room, previous_room, time_elapsed, has_intro_played, "
            "current_objective_id, student_id_obtained "
            "FROM general WHERE save_slot = ?",
            (slot,),
        )
        
        general_info = cursor.fetchone()

        if general_info is None:
            return None
        
        # Get visited rooms
        cursor.execute(
            "SELECT room_name, is_visited FROM room_visited_status "
            "WHERE save_slot = ?",
            (slot,),
        )

        visited_rooms = {row[0]: bool(row[1]) for row in cursor.fetchall()}

        # Get completed rooms
        cursor.execute(
            "SELECT room_name, is_complete FROM room_completed_status "
            "WHERE save_slot = ?",
            (slot,),
        )

        completed_rooms = {row[0]: bool(row[1]) for row in cursor.fetchall()}

        # Get inventory
        cursor.execute(
            "SELECT item FROM inventory WHERE save_slot = ?",
            (slot,),
        )

        inventory_items = [row[0] for row in cursor.fetchall()]

        reconstructed_state = {
            "current_room": general_info[0],
            "previous_room": general_info[1],
            "time_elapsed": general_info[2],
            "has_intro_played": bool(general_info[3]),
            "start_time": time.time(),
            "is_gametime_paused": False,
            "current_objective_id": general_info[4],
            "student_id_obtained": bool(general_info[5]),
            "visited": visited_rooms,
            "completed": completed_rooms,
            "inventory": inventory_items,
        }

        return reconstructed_state
