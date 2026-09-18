# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

from rooms import enterLobby, enterStore, enterLabD2001, enterTeachersRoom1, enterTeachersRoom2
from utilities.clear_screen import clearScreen
import time

start_time = time.time()

state = {
    "current_room": "lobby",
    "previous_room": "lobby",
    "start_time": start_time,
    "coin_balance": 9999,
    # FORMAT: item name, price
    "store_available_items": [
        ["Eeyore plushie", 25],
        ["Delft mug", 10],
    ],
    "visited": {
        "labd2001": False,
        "store": False,
        "projectroom2": False,
        "teachersroom1": False
    },
    "completed": {
        "labd2001": False,
        "store": False,
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

    elif current == "store":
        state["current_room"] = enterStore(state)
    
    elif current == "labd2001":
        state["current_room"] = enterLabD2001(state)
    
    elif current == "teachersroom1":
        state["current_room"] = enterTeachersRoom1(state)
    
    elif current == "teachersroom2":
        state["current_room"] = enterTeachersRoom2(state)

    else:
        print("Unknown room. Exiting game.")
        break


