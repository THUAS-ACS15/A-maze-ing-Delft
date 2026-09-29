# -----------------------------------------------------------------------------
# File: clear_screen.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------


def display_menu(console, commands) -> None:
    """Display the room's command list."""
    console.print("List of all available commands for this room")
    for command, description in commands:
        console.print(f"{'':<3}{command:<20} {description}")
