# -----------------------------------------------------------------------------
# File: get_help.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributor: Gift Odigwe
# -----------------------------------------------------------------------------
"""Shared help display for rooms.

Each room passes its room-specific commands; the defaults are added
automatically. Rooms build their extras list with the same conditionals
they use today (e.g. hide a command once its challenge is completed).
"""

DEFAULT_COMMANDS = [
    ("look around", "Examine the room for clues."),
    ("status", "Show your overall progress."),
    ("go lobby / back", "Leave the room and return to the lobby."),
    ("?", "Show this help message."),
    ("quit", "Quit the game completely."),
]


def get_help(extra_commands=None, include_go_back=True):
    """Display the room's command list: extras first, then the defaults.

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


# Alias preserving a camelCase style used elsewhere in the codebase.
getHelp = get_help
