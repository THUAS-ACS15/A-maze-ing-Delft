# -----------------------------------------------------------------------------
# File: teachersroom4.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
import time

from textwrap import dedent
from art import text2art # type: ignore[import-untyped]
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from utilities.clear_screen import clear_screen
from utilities.display_menu import display_menu
from utilities.loader import loader
from utilities.print_line import print_line
from utilities.save_gui import display_save_menu

header_style = "bold green"

items = ["computer", "paperclip", "note", "mug"]

file_system_without_secret = dedent("""\
.     [blue]just_another_folder[/]           
""")

file_system_with_secret = dedent("""\
.     .azure         .bashrc           .config    .local      .zprofile           super_secret_file.txt
..    .bash_history  .bashrc.original  .docker   .java        .profile           .sudo_as_admin_successful 
.aws  .bash_logout   .cache            .emacs.d  .lesshst     
""").strip()

room_commands = [
    (
        "look around",
        "Nose around the abandoned desk. The mug is off-limits. Everything else… gray " "area.",
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
        "pause/save",
        "Pause the game or save your progress.",
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
    top_line = f"{CYAN}┌──({BLUE}{username}㉿{hostname}{CYAN})-[{BOLD}{path}{RESET}" f"{CYAN}]{RESET}"

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


def _show_goodbye() -> None:
    """Splash shown when leaving the computer (shutdown or logout)."""
    clear_screen()
    message = text2art("Good bye!", font="univers", chr_ignore=True)
    print_line(message, delay=0.002)
    time.sleep(1)
    clear_screen()


def enter_teachers_room4(state: dict) -> str:
    """Greet the player in Teachers Room 4 and send them back to the Lobby."""
    clear_screen()
    console = Console(legacy_windows=False)

    # Display loading state
    loader(label="Loading teachers room...")

    print_line("[cyan]You step into Teachers Room 4. 🎉[/]")
    print_line("Plot twist: the teacher saw you coming and vanished faster than free pizza at " "a student event.")
    print_line('A note on the desk reads: "Gone. Probably. Don\'t touch my mug. — The Teacher"')
    print_line("No lessons, no questions — put your feet up and get comfortable. You earned " "this break. ☕")
    state["previous_room"] = "teachersroom4"

    choice = input(">")
    while choice not in ("leave", "exit"):
        match choice:
            case "?" | "help":
                display_menu(console, room_commands)
            case "pause" | "save":
                display_save_menu(state)
            case "get comfortable":
                loader(label="taking a sit...")
                print_line("You made a good choice. The chair spins. Life is good. ☕")
                seated = input(">")
                while seated:
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
                                taken = input(">")
                                state.setdefault(
                                    "inventory",
                                    [],
                                ).append(taken)
                                print_line(f"You pocket the {taken}. The teacher will never " f"know.")
                        case "boot computer":
                            clear_screen()
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
                            clear_screen()
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
                            clear_screen()
                            print_line(
                                "Viola! you are half way in! Now explore the file system to see if you find "
                                "anything interesting.",
                                delay=0.015,
                            )
                            time.sleep(1)
                            print_line(text="[bold green]NIXOS // teacher-pc[/]")
                            print_line("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
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
                            computer = input(_get_prompt())
                            while computer != "shutdown":
                                match computer:
                                    case "?" | "help":
                                        display_menu(
                                            console,
                                            computer_commands,
                                        )
                                    case "ls":
                                        print_line(file_system_without_secret)
                                    case "ls -a":
                                        print_line(file_system_with_secret)
                                    case "cat super_secret_file.txt":
                                        code = """
                                        # Congrats you completed this challenge!
                                        """
                                        syntax_disp = Syntax(
                                            code,
                                            "python",
                                            theme="monokai",
                                            line_numbers=True,
                                            highlight_lines={1},  # Highlights line 1
                                        )
                                        time.sleep(0.4)
                                        console.print(syntax_disp)
                                        time.sleep(0.4)
                                        if "super_secret_file.txt" not in state.get("inventory", []):
                                            state.setdefault("inventory", []).append("super_secret_file.txt")
                                            print_line("[yellow]New item added to inventory[/]")
                                    case "clear":
                                        clear_screen()
                                    case _:
                                        print_line("[red]You do not have the permission to execute this command.[/]")

                                if computer != "shutdown":
                                    print_line("[bold green]NIXOS // teacher-pc[/]")
                                    print_line("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
                                    computer = input(_get_prompt())
                            _show_goodbye()
                            break
                        case "stand up":
                            break
            case "look around":
                _show_desk(console, state)
        choice = input(">")
    return "labd2001"
