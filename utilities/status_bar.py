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
import shutil

# This dict just matches the room identifiers to a fancier display name, for use in updateStatusBar()
room_fancy_names = {
    "lobby": "🏠 Lobby",
    "labd2001": "🧪 Lab D2.001",
    "projectroom2": "🖥️ Project Room 2",
    "teachersroom1": "👩 Teacher's Room 1",
    "teachersroom2": "👩 Teacher's Room 2"
}

def calculateTimePlayed(start_time: float) -> str:
    """
    Calculates the time played in seconds since the start_time.
    
    This function takes the start_time stored in the state dict and calculates the time played in seconds since that time.
    If needed, it also separates by hours and minutes, and returns it in string form.
    
    Inputs:
        start_time (float): The start time in seconds.
    
    Outputs:
        str: The time played, separated if necessary.
    """

    current_time = time.time()

    time_played = math.ceil(current_time - start_time)

    final_time = ''
    # Separate in hours, minutes, seconds
    if time_played > 3600:
        hours = time_played // 3600
        minutes = (time_played % 3600) // 60
        seconds = time_played % 60
        final_time = f"{hours}h {minutes}m {seconds}s"
    elif time_played > 60:
        minutes = time_played // 60
        seconds = time_played % 60
        final_time = f"{minutes}m {seconds}s"
    else:
        final_time = f"{time_played}s"

    return final_time

def updateStatusBar(state: dict) -> None:
    current_room = state["current_room"]
    room_name = room_fancy_names[current_room]
    time_played = calculateTimePlayed(state["start_time"])

    # Starting / ending rooms don't have challenges, so display a special message for them
    if current_room in ["lobby"]:
        room_completion = "⭐ Special Room"
    # If the room is a challenge room, display whether the room is marked as completed in the state dict
    else:
        if state["completed"][current_room]:
            room_completion = "✅ Room complete!"
        else:
            room_completion = "❌ Room not complete."

    # Get terminal size, while falling back to the default of 126x20, we only need columns though
    terminal_width = shutil.get_terminal_size(fallback=(126, 20)).columns

    # Stats to be displayed
    left_status_data = f"{room_name} | {room_completion}"
    right_status_data = f"🪙 {state['coin_balance']} ⌛ {time_played}"

    # Calculate the gap between the left and right status data, remove 5 because the 5 emojis used take up 2 chars each
    gap = terminal_width - 5 - len(left_status_data) - len(right_status_data)

    print(f"{left_status_data}{' ' * gap}{right_status_data}")
    print(f"{'█' * terminal_width}\n")
