# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import time
from utilities.clear_screen import clearScreen
from rooms import (
    enterLobby,
    enterStore,
    enterLabD2001,
    enterTeachersRoom1,
    enterTeachersRoom2,
    enterProjectRoom1,
    enterProjectRoom2,
    enterFrontDesk,
    enterClassroomD2015,
    enterClassroomD2035
)

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": "lobby",
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
        "classroomd2015": False,
        "classroomd2035": False
    },
    "inventory": []
}

clearScreen()

while True:
    current = state["current_room"]

    if current == "lobby":
        state["current_room"] = enterLobby(state)

    elif current == "store":
        state["current_room"] = enterStore(state)

    elif current == "labd2001":
        state["current_room"] = enterLabD2001(state)

    elif current == "teachersroom1":
        state["current_room"] = enterTeachersRoom1(state)

    elif current == "teachersroom2":
        state["current_room"] = enterTeachersRoom2(state)

    elif current == "projectroom2":
        state["current_room"] = enterProjectRoom2(state)

    elif current == "projectroom1":
        state["current_room"] = enterProjectRoom1(state)

    elif current == "frontdesk":
        state["current_room"] = enterFrontDesk(state)

    elif current == "classroomd2015":
        state["current_room"] = enterClassroomD2015(state)

    elif current == "classroomd2035":
        state["current_room"] = enterClassroomD2035(state)

    elif current in ["quit", "exit"]:
        print("Exiting... goodbye and thanks for playing!")
        break

    else:
        print(f"Unknown room '{current}'. Returning to Lobby...")
        time.sleep(1.0)
        state["current_room"] = "lobby"
