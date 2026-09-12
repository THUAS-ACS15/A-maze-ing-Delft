# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

from rooms import enterLobby, enterLabD2001
from utilities.utils import clearScreen
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

clearScreen(state)
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

    else:
        print("Unknown room. Exiting game.")
        break
