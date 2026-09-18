# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

from rooms import enterLobby, enterLabD2001, enterTeachersRoom1, enterTeachersRoom2
from utilities.clear_screen import clearScreen
import time

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": "lobby",
    "start_time": start_time,
    "coin_balance": 0,
    "visited": {
        "labd2001": False,
        "projectroom2": False,
        "teachersroom1": False
    },
    "completed": {
        "labd2001": False,
        "projectroom2": False,
        "teachersroom1": False
    },
    "inventory": []
}

clearScreen()

while True:
    current = state["current_room"]

    if current == "lobby":
        state["current_room"] = enterLobby(state)

    elif current == "labd2001":
        state["current_room"] = enterLabD2001(state)
    elif current == "teachersroom1":
        state["current_room"] = enterTeachersRoom1(state)
    elif current == "teachersroom2":
        state["current_room"] = enterTeachersRoom2(state)

    else:
        print("Unknown room. Exiting game.")
        break


