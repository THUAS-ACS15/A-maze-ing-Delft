# -----------------------------------------------------------------------------
# File: teachersroom4.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
import time

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from art import *

from utilities.clear_screen import clearScreen
from utilities.display_menu import display_menu
from utilities.loader import loader
from utilities.print_line import print_line
from utilities.prompt import prompt

header_style = "bold green"

items = ["computer", "paperclip", "note", "mug"]

room_commands = [
    (
        "look around",
        "Nose around the abandoned desk. The mug is off-limits. Everything else… gray area.",
    ),
    (
        "get comfortable",
        "Sink into the teacher's spinny chair. Spin tax: zero.",
    ),
    (
        "help/?",
        "Lost? Here's the map. Don't tell the teacher you needed it.",
    ),
    (
        "leave/exit",
        "Slip back to the lobby before the footsteps return.",
    ),
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
    (
        "stand up",
        "Abandon the spinny chair. It will miss you.",
    ),
    (
        "pick up",
        "Pocket something from the desk. The teacher is gone — probably.",
    ),
    (
        "boot computer",
        "Snoop on the teacher's unfinished work. Password willing.",
    ),
    (
        "help/?",
        "Lost in comfort? Here's the map.",
    ),
]

# Style & Color definitions
RESET = "\033[0m"
CYAN = "\033[36m"
BLUE = "\033[34m"
BOLD = "\033[1m"


def _get_prompt(username: str = "username", hostname: str = "teacher4", path: str = "~") -> str:
    # Top line: ┌──(username㉿hostname)-[path]
    top_line = f"{CYAN}┌──({BLUE}{username}㉿{hostname}{CYAN})-[{BOLD}{path}{RESET}{CYAN}]{RESET}"

    # Bottom line: └─$
    bottom_line = f"{CYAN}└─{BLUE}${RESET} "

    return f"{top_line}\n{bottom_line}"


def _remaining_items(state: dict) -> list:
    """Items still on the desk (taken ones stay in the inventory)."""
    return [item for item in items if item not in state.get("inventory", [])]


def _show_desk(console: Console, state: dict) -> None:
    """Show the desk contents in a panel."""
    remaining = _remaining_items(state)
    if remaining:
        console.print(
            Panel(
                "\n".join(f"- {item}" for item in remaining),
                title="On the desk",
            )
        )
    else:
        console.print(
            Panel(
                "Picked clean. The teacher will notice. Probably.",
                title="On the desk",
            )
        )


def enter_teachers_room_4(state: dict) -> str:
    """Greet the player in Teachers Room 4 and send them back to the Lobby."""
    clearScreen()
    console = Console(legacy_windows=False)

    # Display loading state
    loader(label="Loading teachers room...")

    print_line("[cyan]You step into Teachers Room 4. 🎉[/]")
    print_line(
        "Plot twist: the teacher saw you coming and vanished faster than free pizza at a student event."
    )
    print_line(
        'A note on the desk reads: "Gone. Probably. Don\'t touch my mug. — The Teacher"'
    )
    print_line(
        "No lessons, no questions — put your feet up and get comfortable. You earned this break. ☕"
    )
    state["previous_room"] = "teachersroom4"

    choice = input(":")
    while choice not in ("leave", "exit"):
        match choice:
            case "?" | "help":
                display_menu(console, room_commands)
            case "get comfortable":
                loader(label="taking a sit...")
                print_line("You made a good choice. The chair spins. Life is good. ☕")
                seated_choices = [
                    "stand up",
                    "pick up",
                    "boot computer",
                    "help",
                    "?",
                ]
                seated = input(":")
                while seated != "stand up":
                    match seated:
                        case "?" | "help":
                            display_menu(
                                console,
                                position_commands,
                            )
                        case "pick up":
                            remaining = _remaining_items(state)
                            if not remaining:
                                print_line("Nothing left but crumbs. Leave those too.")
                            else:
                                taken = input(_)
                                state.setdefault(
                                    "inventory",
                                    [],
                                ).append(taken)
                                print_line(
                                    f"You pocket the {taken}. The teacher will never know."
                                )
                        case "boot computer":
                            clearScreen()
                            sequence = [
                                "systemd-boot → NixOS Generation 42",
                                "<<< NixOS Stage 1 >>> loading kernel modules",
                                "LUKS unlock… skipped (no secrets here. Probably.)",
                                "Mounting /nix/store from /dev/sda1",
                                "Stage 2 activation: /etc, users, secrets",
                                "starting systemd... (PID 1)",
                                "Reached graphical.target",
                            ]
                            loader(
                                loading_time=1.2,
                                label="Booting up the computer...",
                                console=console,
                                mode="PROGRESS",
                                sequence=sequence,
                            )
                            clearScreen()
                            time.sleep(1)
                            print_line(
                                text2art(
                                    "NIX OS",
                                    font="univers",
                                    chr_ignore=True,
                                ),
                                delay=0.002,
                            )
                            time.sleep(2)
                            clearScreen()
                            print_line(
                                "Viola! you are half way in before you get in, you need to figure out the username and password. Get creative!",
                                delay=0.015,
                            )
                            time.sleep(1)
                            print_line(text="[bold green]NIXOS // teacher-pc[/]")
                            print_line("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
                            print_line("Enter username and password to continue...")
                            computer_choices = [
                                "username",
                                "password",
                                "shutdown",
                                "help",
                                "?",
                            ]
                            computer_commands = [
                                (
                                    "shutdown",
                                    "Check the abandoned desk. The mug is off-limits—everything else is fair game.",
                                ),
                                (
                                    "help/?",
                                    "Need a hint? Here’s the map. And no, you didn’t need to ask the teacher.",
                                ),
                            ]
                            attempt = 0
                            computer = input("username: ")
                            while computer != "shutdown":
                                match computer:
                                    case "?" | "help":
                                        display_menu(
                                            console,
                                            computer_commands,
                                        )
                                    case "username":
                                        attempt = 0
                                        print_line(
                                            "Good job! now the final lap. just the password and you're in. make this count"
                                        )
                                        print_line("[bold green]NIXOS // teacher-pc[/]")
                                        print_line("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
                                        print_line(
                                            "Enter username and password to continue..."
                                        )
                                        attempt = 0
                                        password = input("password: ")
                                        while password != "shutdown":
                                            match password:
                                                case "?" | "help":
                                                    display_menu(
                                                        console,
                                                        computer_commands,
                                                    )
                                                case "password":
                                                    logged_in_choices = [
                                                        "logout",
                                                        "help",
                                                        "?",
                                                    ]
                                                    print_line(
                                                        "Congrats, you completed this challenge! Not once did I doubt you",
                                                        delay=0.015,
                                                    )
                                                    state.setdefault("inventory", []).append("teacher_password")
                                                    print_line(
                                                        "[yellow]New item added to inventory[/]"
                                                    )
                                                    print_line(
                                                        "[bold green]NIXOS // teacher-pc[/]"
                                                    )
                                                    print_line(
                                                        "[dim]NixOS 26.05 (Linux 6.12.1)[/]"
                                                    )
                                                    logged_in = input(_get_prompt())
                                                    while logged_in not in ("logout", "shutdown"):
                                                        match logged_in:
                                                            case "?" | "help":
                                                                display_menu(
                                                                    console,
                                                                    computer_commands,
                                                                )
                                                            case _:
                                                                display_menu(
                                                                    console,
                                                                    computer_commands,
                                                                )
                                                        logged_in = input(_get_prompt(), )
                                                    computer = "shutdown"
                                                    break
                                                case _:
                                                    if attempt == 0:
                                                        print_line(
                                                            "Invalid Password! Try again"
                                                        )
                                                        attempt += 1
                                                    elif attempt == 1:
                                                        print_line(
                                                            "Invalid password! Try again. It is alot easier than you think"
                                                        )
                                                        attempt += 1
                                                    elif attempt == 2:
                                                        print_line(
                                                            "Invalid password! Try again"
                                                        )
                                                        print_line(
                                                            "[yellow]hint[/]! imagine a world where your name disappears and you have to type one magic word to reveal it?"
                                                        )
                                                        attempt += 1
                                                    else:
                                                        print_line(
                                                            "Invalid password! Try again"
                                                        )
                                                        print_line(
                                                            "[yellow]hint:[/] before entering any account, whats the first gate you pass?"
                                                        )
                                                        print_line(
                                                            "[yellow]hint:[/] What single wor is the DNA of ever account you ever created?"
                                                        )
                                                        attempt += 1
                                            if password != "shutdown" and computer != "shutdown":
                                                password = input("Password: ")
                                        if password == "shutdown":
                                            computer = "shutdown"

                                    case _:
                                        if attempt == 0:
                                            print_line("Invalid username! Try again")
                                            attempt += 1
                                        elif attempt == 1:
                                            print_line(
                                                "Invalid username! Try again. It is alot easier than you think"
                                            )
                                            attempt += 1
                                        elif attempt == 2:
                                            print_line("Invalid username! Try again")
                                            print_line(
                                                "[yellow]hint[/]! imagine a world where your name disappears and you have to type one magic word to reveal it?"
                                            )
                                            attempt += 1
                                        else:
                                            print_line("Invalid username! Try again")
                                            print_line(
                                                "[yellow]hint:[/] before entering any account, whats the first gate you pass?"
                                            )
                                            print_line(
                                                "[yellow]hint:[/] What single wor is the DNA of ever account you ever created?"
                                            )
                                            attempt += 1
                                if computer != "shutdown":
                                    computer = input("Username: ")
                    if seated != "stand up":
                        seated = input("_")
            case "look around":
                _show_desk(console, state)
        choice = input("_")
    return "lobby"


enterTeachersRoom4 = enter_teachers_room_4
