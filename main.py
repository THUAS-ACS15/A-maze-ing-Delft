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

    elif current in ["projectroom1", "project_room_1"]:
        state["current_room"] = enterProjectRoom1(state)

    elif current in ["frontdesk", "front_desk"]:
        state["current_room"] = enterFrontDesk(state)

    elif current in ["classroomd2015", "classroom_d2.015", "classroom_d2015"]:
        if enterClassroomD2015:
            state["current_room"] = enterClassroomD2015(state)
        else:
            print("Classroom D2.015 could not be loaded.")
            state["current_room"] = "lobby"

    elif current in ["classroomd2035", "classroom_d2035", "classroom_d2.035"]:
        state["current_room"] = enterClassroomD2035(state)

    elif current in ["quit", "exit"]:
        print("Thank you for playing A-maze-ing Delft!")
        break

    else:
        print(f"Unknown room '{current}'. Returning to Lobby...")
        time.sleep(1.0)
        state["current_room"] = "lobby"
