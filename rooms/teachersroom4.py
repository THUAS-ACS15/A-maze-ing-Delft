# -----------------------------------------------------------------------------
# File: teachersroom4.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from utilities.clear_screen import clearScreen
from utilities.display_menu import display_menu
from utilities.print_line import print_line
from utilities.prompt import prompt

header_style = "bold green"

items = ["computer", "paperclip", "note", "mug"]

room_commands = [
    ("look around", "Nose around the abandoned desk. The mug is off-limits. Everything else… gray area."),
    ("get comfortable", "Sink into the teacher's spinny chair. Spin tax: zero."),
    ("help/?", "Lost? Here's the map. Don't tell the teacher you needed it."),
    ("leave/exit", "Slip back to the lobby before the footsteps return."),
]

commands = [
    "look around",
    "get comfortable",
    "?",
    "help",
    "leave",
    "exit",
]

position_commands = [
    ("stand up", "Abandon the spinny chair. It will miss you."),
    ("pick up", "Pocket something from the desk. The teacher is gone — probably."),
    ("boot up computer", "Snoop on the teacher's unfinished work. Password willing."),
    ("help/?", "Lost in comfort? Here's the map."),
]


def _remaining_items(state: dict) -> list:
    """Items still on the desk (taken ones stay in the inventory)."""
    return [item for item in items if item not in state.get("inventory", [])]


def _show_desk(console: Console, state: dict) -> None:
    """Show the desk contents in a panel."""
    remaining = _remaining_items(state)
    if remaining:
        console.print(Panel("\n".join(f"- {item}" for item in remaining), title="On the desk"))
    else:
        console.print(Panel("Picked clean. The teacher will notice. Probably.", title="On the desk"))



def enter_teachers_room_4(state: dict) -> str:
    """Greet the player in Teachers Room 4 and send them back to the Lobby."""
    clearScreen()
    console = Console(legacy_windows=False)

    print_line(console, "\nYou step into Teachers Room 4. 🎉", header_style)
    print_line(console, "Plot twist: the teacher saw you coming and vanished faster than free pizza at a student event.")
    print_line(console, "A note on the desk reads: \"Gone. Probably. Don't touch my mug. — The Teacher\"")
    print_line(console, "No lessons, no questions — put your feet up and get comfortable. You earned this break. ☕")
    state["previous_room"] = "teachersroom4"

    choice = prompt(console, commands)
    while choice not in ("leave", "exit"):
        match choice:
            case "?" | "help":
                display_menu(console, room_commands)
            case "get comfortable":
                print_line(console, "You made a good choice. The chair spins. Life is good. ☕")
                seated_choices = ["stand up", "pick up", "boot up computer", "help", "?"]
                display_menu(console, position_commands)
                seated = prompt(console, seated_choices)
                while seated != "stand up":
                    match seated:
                        case "?" | "help":
                            display_menu(console, position_commands)
                        case "pick up":
                            remaining = _remaining_items(state)
                            if not remaining:
                                print_line(console, "Nothing left but crumbs. Leave those too.")
                            else:
                                taken = Prompt.ask("Take what?", choices=remaining, show_choices=False, console=console)
                                state.setdefault("inventory", []).append(taken)
                                print_line(console, f"You pocket the {taken}. The teacher will never know.")
                        case "boot up computer":
                            print_line(console, "Loading boot sequence... password protected, obviously.")
                    seated = prompt(console, seated_choices, "stand up")
            case "look around":
                _show_desk(console, state)
        choice = prompt(console, commands)
    return "lobby"

enterTeachersRoom4 = enter_teachers_room_4
