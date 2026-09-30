# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import time

from rooms.dispatcher import enter_room
from utilities.clear_screen import clear_screen

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": None,
    "start_time": start_time,
    "is_gametime_paused": False,
    "coin_balance": 0,
    "student_id_obtained": False,
    # Format: item_name, item_price
    "store_available_items": [
        ["Eeyore plushie", 25],
        ["Delft mug", 10],
    ],
    "completed": {
        "labd2001": False,
        "store": False,
        "projectroom1": False,
        "projectroom2": False,
        "teachersroom1": False,
        "teachersroom2": False,
        "teachersroom4": False,
        "frontdesk": False,
        "equinoxstudentsociety": False,
        "classroomd2015": False,
        "classroomd2035": False,
    },
    "equinox_coins_claimed": False,
    "inventory": [],
}


def main():
    clear_screen()

    # Main room-navigation loop.
    # Repeatedly reads the player's current room from state, falls back to "lobby"
    # if the value is missing or invalid, and calls enter_room() to determine the
    # next room. The loop continues until enter_room() returns "quit" or "exit",
    # at which point the game ends. Otherwise, the returned room is saved back into
    # state["current_room"] for the next iteration.
    while True:
        current = state.get("current_room", "lobby")
        if not isinstance(current, str):
            current = "lobby"
        next_room = enter_room(current, state)
        if next_room in ("quit", "exit"):
            break
        state["current_room"] = next_room


if __name__ == "__main__":
    main()