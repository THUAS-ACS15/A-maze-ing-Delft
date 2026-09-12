# -----------------------------------------------------------------------------
# File: status_bar.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

import time
import math

room_fancy_names = {
    "lobby": "🏠 Lobby",
    "labd2001": "🧪 Lab D2.001"
}

def update_status_bar(state):
    current_room = state["current_room"]
    room_name = room_fancy_names[current_room]
    time_played = math.ceil(time.time() - state["start_time"])
    if current_room in ["lobby"]:
        room_completion = "⭐ Special Room              "
    else:
        if state["visited"][current_room]:
            room_completion = "✅ Room complete!       "
        else:
            room_completion = "❌ Room not complete.   "

    print(f"{room_name} | {room_completion}                                                                       ⌛ {time_played}s")
    print("████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████\n")