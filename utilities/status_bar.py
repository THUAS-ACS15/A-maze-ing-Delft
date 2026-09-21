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
    "store": "🏪 Store",
    "projectroom2": "🖥️ Project Room 2",
    "teachersroom1": "👩 Teacher's Room 1",
    "teachersroom2": "👩 Teacher's Room 2",
    "projectroom1": "🔐 Project Room 1",
    "frontdesk": "🛎️ Front Desk",
    "classroomd2015": "🤖 Classroom D2.015",
    "classroomd2035": "📚 Classroom D2.035"
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

def getExplorationPercent(state: dict) -> float:
    """
    Calculates the percentage of the map that has been explored.

    This function takes the state dict and calculates the percentage of the map that has been explored by counting the number of completed rooms and dividing by the total number of rooms.

    Inputs:
        state (dict): The current game state.

    Outputs:
        float: The percentage of the map that has been explored, rounded to 2 decimal places.
    """
    completed_dict = state["completed"]

    total_rooms = len(completed_dict)
    completed_rooms = sum(completed_dict.values()) # This counts the number of True values (i.e. completed rooms)

    exploration_percent = (completed_rooms / total_rooms) * 100
    exploration_percent = round(exploration_percent, 2) # Round to 2 decimals

    return exploration_percent

def updateStatusBar(state: dict) -> None:
    """
    Updates the status bar with the current room, completion status, coin balance, and time played.

    This function takes the state dict and uses it to display the current room, the total exploration percentage,
    whether the room is completed, the coin balance, and the time played since the start of the game.

    Inputs:
        - state (dict): The current game state.

    Outputs: NONE
    """
    current_room = state["current_room"]

    try:
        room_name = room_fancy_names[current_room]
    except KeyError:
        room_name = "⚠️ ROOM FANCY NAME NOT FOUND"

    time_played = calculateTimePlayed(state["start_time"])
    exploration_percent = getExplorationPercent(state)
    
    # Starting / ending rooms don't have challenges, so display a special message for them
    if current_room in ["lobby"]:
        room_completion = "⭐ Special Room"
    # If the room is a challenge room, display whether the room is marked as completed in the state dict
    else:
        try:
            if state["completed"][current_room]:
                room_completion = "✅ Room complete!"
            else:
                room_completion = "❌ Room not complete."
        except KeyError:
            room_completion = "⚠️ ROOM NOT IN STATE DICT"

    # Get terminal size, while falling back to the default of 126x20, we only need columns though
    terminal_width = shutil.get_terminal_size(fallback=(126, 20)).columns

    # Stats to be displayed
    left_status_data = f"{room_name} | {exploration_percent}% explored | {room_completion}"
    right_status_data = f"🪙 {state['coin_balance']} ⌛ {time_played}"

    # Calculate the gap between the left and right status data, remove 5 because the 5 emojis used take up 2 chars each
    gap = terminal_width - 5 - len(left_status_data) - len(right_status_data)

    print(f"{left_status_data}{' ' * gap}{right_status_data}")
    print(f"{'█' * terminal_width}\n")
