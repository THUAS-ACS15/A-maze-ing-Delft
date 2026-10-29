# -----------------------------------------------------------------------------
# File: centralized_commands.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributor: Gift Odigwe, Leon
# -----------------------------------------------------------------------------

"""
Shared help display for rooms.

Each room passes its room-specific commands; the defaults are added
automatically. Rooms build their extras list with the same conditionals
they use today (e.g. hide a command once its challenge is completed).
"""

DEFAULT_COMMANDS = [
    (
        "?",
        "Show this help message."
    ),
    (
        "go",
        "Go to another room.",
    ),
    (
        "look around",
        "Examine the room for clues.",
    ),
    (
        "status/check status", 
        "Show your overall progress."
    ),
    (
        "inv/inventory",
        "Show your inventory."
    ),
    (
        "save/pause",
        "Save your progress."
    ),
    (
        "quit",
        "Quit the game completely."
    ),
]

def display_help(extra_commands: list[tuple[str, str]] | None = None, include_go_back: bool = True) -> None:
    """
    Displays the room's command list: extras first, then the defaults.

    Inputs:
        - extra_commands: list of (command, description) tuples with the
          room-specific commands. Pass [] or None when there are none.
        - include_go_back: set to False for rooms where the default
          "go lobby / back" line does not apply (e.g. the lobby itself,
          which passes its own "go <room name>" extra instead).

    Outputs: NONE
    """
    commands = list(extra_commands or [])
    for command, description in DEFAULT_COMMANDS:
        if command == "go lobby / back" and not include_go_back:
            continue
        commands.append((command, description))

    print("Available commands:")
    for command, description in commands:
        print(f"- {command:<18}: {description}")

def display_look_around(state: str):
    pass