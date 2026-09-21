# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

from rooms import enterLobby, enterLabD2001, enterTeachersRoom1, enterTeachersRoom2, enterProjectRoom2
from utilities.clear_screen import clearScreen
import time

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": "lobby",
    "start_time": start_time,
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
print("****************************************************************************")
print("*                      Welcome to the School Maze!                         *")
print("*        Your goal is to explore all important rooms in the school.        *")
print("*    You may need to solve challenges to collect items and unlock rooms.   *")
print("*               Once you've visited all rooms, you win!                    *")
print("****************************************************************************")

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
    elif current == "projectroom2":
        state["current_room"] = enterProjectRoom2(state)

    else:
        print("Unknown room. Exiting game.")
        break


