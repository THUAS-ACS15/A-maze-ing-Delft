# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import time
from utilities.clear_screen import clearScreen
from rooms.dispatcher import enter_room

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": None,
    "start_time": start_time,
    "coin_balance": 0,
    "student_id_obtained": False,
    # Format: item_name, item_price
    "store_available_items": [
        ["Eeyore plushie", 25],
        ["Delft mug", 10],
    ],
    "visited": {
        "lobby": True,
        "labd2001": False,
        "store": False,
        "projectroom1": False,
        "projectroom2": False,
        "teachersroom1": False,
        "teachersroom2": False,
        "frontdesk": False,
        "equinoxstudentsociety": False,
        "classroomd2015": False,
        "classroomd2035": False
    },
    "completed": {
        "labd2001": False,
        "store": False,
        "projectroom1": False,
        "projectroom2": False,
        "teachersroom1": False,
        "teachersroom2": False,
        "frontdesk": False,
        "equinoxstudentsociety": False,
        "classroomd2015": False,
        "classroomd2035": False
    },
    "inventory": []
}

clearScreen()

while True:
    next_room = enter_room(state["current_room"], state)
    if next_room in ("quit", "exit"):
        break
    state["current_room"] = next_room
