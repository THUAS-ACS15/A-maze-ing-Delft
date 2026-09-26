# -----------------------------------------------------------------------------
# File: teachersroom4.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
from rich.console import Console
from utilities.clear_screen import clearScreen
from utilities.print_line import print_line
from rich.prompt import Prompt

HEADER_STYLE = "bold green"

HELP_COMMANDS = [
    ("get comfortable", "Take a seat and relax"),
    ("leave", "Head back to the Lobby"),
    ("?", "Show this help message."),
    ("help", "Show this help message."),
]


def _show_menu(console) -> None:
    """Display the room's command list."""
    console.print("Available commands:")
    for command, description in HELP_COMMANDS:
        console.print(f"- {command:<17}: {description}")
def enter_teachers_room_4(state: dict) -> str:
    """Greet the player in Teachers Room 4 and send them back to the Lobby."""
    clearScreen()
    console = Console(legacy_windows=False)

    print_line(console, "\nYou step into Teachers Room 4. 🎉", HEADER_STYLE, 0.015)
    print_line(console, "Plot twist: the teacher saw you coming and vanished faster than free pizza at a student event.", "", 0.015)
    print_line(console, "A note on the desk reads: \"Gone. Probably. Don't touch my mug. — The Teacher\"", "", 0.015)
    print_line(console, "No lessons, no questions — put your feet up and get comfortable. You earned this break. ☕", "", 0.015)
    state["previous_room"] = "teachersroom4"

    choices = [command for command, _ in HELP_COMMANDS]
    choice = Prompt.ask(
        "Command",
        choices=choices,
        default="leave",
        show_choices=False,
        console=console,
    )
    while choice != "leave":
        if choice in ("?", "help"):
            _show_menu(console)
        else:  # get comfortable
            print_line(console, "You made a good choice. The chair spins. Life is good. ☕", "", 0.015)
        choice = Prompt.ask(
            "Command",
            choices=choices,
            default="leave",
            show_choices=True,
            console=console,
        )
    return "lobby"

enterTeachersRoom4 = enter_teachers_room_4