# -----------------------------------------------------------------------------
# File: teachers_room_4.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributor: Gift Odigwe
# -----------------------------------------------------------------------------
"""Teacher Room 4: desk interaction plus a NixOS terminal challenge.

Inspecting the room computer boots a virtual NixOS shell where the player
explores an in-memory filesystem and hunts for a hidden secret file. Reading
that file awards the Encrypted API & Prompt USB to the inventory exactly once,
marks the room as completed and advances the objective.
"""
import time

from rich.console import Console
from rich.text import Text

from assets.nixos import nixos as nixos_logo

from data.story_dialogue_bank import story_dialogue_bank

from utilities.clear_screen import clear_screen
from utilities.colors import CYAN, BLUE, BOLD, RESET
from utilities.display_menu import display_menu
from utilities.game_map import display_map
from utilities.loader import loader
from utilities.print_helpers import (
    print_assembly_part_obtained,
    print_current_objective,
    print_dialogue,
)
from utilities.save_gui import display_save_menu
from utilities.shell import VirtualShell

header_style = "bold green"

room_dialogue_bank = story_dialogue_bank["rooms"]["teachersroom4"]

# Absolute virtual path of the only file that grants the USB reward.
SECRET_PATH = "/home/teacher/.secret/super_secret_file.txt"

# Item awarded on the first read of the secret file.
REWARD_ITEM = "Encrypted API & Prompt USB"

# Boot log lines shown by the loader before the terminal opens.
computer_sequence = [
    "systemd-boot → NixOS Generation 42",
    "<<< NixOS Stage 1 >>> loading kernel modules",
    "LUKS unlock… skipped (no secrets here. Probably.)",
    "Mounting /nix/store from /dev/sda1",
    "Stage 2 activation: /etc, users, secrets",
    "starting systemd... (PID 1)",
    "Reached graphical.target",
]

# Virtual filesystem: dicts are directories, strings are file contents.
FILESYSTEM = {
    "etc": {
        "hostname": "teacher-pc\n",
        "passwd": "root:x:0:0:root:/root:/bin/bash\nteacher:x:1000:100:Teacher:/home/teacher:/bin/bash\n",
        "nixos": {
            "configuration.nix": (
                "{ config, pkgs, ... }:\n{\n  networking.hostName = \"teacher-pc\";\n"
                "  users.users.teacher.isNormalUser = true;\n  system.stateVersion = \"26.05\";\n}\n"
            ),
        },
    },
    "home": {
        "teacher": {
            "Documents": {
                "grading_notes.txt": "Grade fairly. Coffee first.\n",
                "exam_draft.txt": "Question 1: Why is the maze so confusing?\n",
                ".notes.txt": (
                    "I moved the schematic somewhere out of sight.\n"
                    "Hidden things tend to live in hidden places.\n"
                ),
            },
            "Downloads": {
                "lecture_slides.pdf": "[binary data omitted]\n",
            },
            "Projects": {
                "maze_generator": {
                    "README.md": "A tiny maze generator. Work in progress.\n",
                },
            },
            ".config": {
                "nixpkgs": {"config.nix": "{ allowUnfree = true; }\n"},
            },
            ".secret": {
                "super_secret_file.txt": (
                    "Congratulations!\n"
                    "You found the A-maze-ing Delft schematic.\n"
                    "The Encrypted API & Prompt USB has been copied to your inventory.\n"
                ),
            },
            ".bashrc": "# ~/.bashrc\nalias ll='ls -l'\n",
            "README.txt": (
                "Welcome to teacher-pc. Type 'help' to see the available commands.\n"
                "Tip: not every file shows up in a plain ls. Try 'ls -a' or 'find'.\n"
            ),
        },
    },
    "nix": {
        "store": {
            "nixos-system": {
                "README": "This is the NixOS system closure. Nothing to see here.\n",
            },
        },
    },
    "var": {
        "log": {
            "nixos.log": "activating the configuration...\nsetting up /etc...\nsystem activated.\n",
        },
    },
}

console = Console()

room_commands = [
    (
        "use computer",
        "Boot the teacher's computer and explore the NixOS terminal.",
    ),
    (
        "help/?",
        "Show the available commands.",
    ),
    (
        "pause/save",
        "Pause the game or save your progress.",
    ),
    (
        "leave/exit",
        "Return to the East Corridor.",
    ),
]


def _prompt_text(shell: VirtualShell) -> str:
    """Build the two-line colored terminal prompt.

    Args:
        shell: Shell providing the user, host, and display directory.

    Returns:
        The prompt string passed to the input reader.
    """
    top_line = f"{CYAN}┌──({BLUE}{shell.user}㉿{shell.hostname}{CYAN})-[{BOLD}{shell.display_cwd}{RESET}{CYAN}]{RESET}"
    bottom_line = f"{CYAN}└─{BLUE}${RESET} "
    return f"{top_line}\n{bottom_line}"


def _reward(state: dict, write_output=None) -> None:
    """Grant the USB reward on first read of the secret file.

    Always marks the room as completed; appends the reward to the inventory
    and advances the objective only when it is not already there.

    Args:
        state: The current game state.
        write_output: Callable receiving the status message. Defaults to
            the module console printer.
    """
    write_output = write_output or console.print
    inventory = state["inventory"]
    state["completed"]["teachersroom4"] = True
    if REWARD_ITEM in inventory:
        write_output(f"[dim]The {REWARD_ITEM} is already in your inventory.[/]")
        return
    inventory.append(REWARD_ITEM)
    state["current_objective_id"] += 1
    write_output(f"[bold green]{REWARD_ITEM} added to your inventory![/]")
    print_assembly_part_obtained(f"(+ {REWARD_ITEM})")
    print_current_objective(state)


def run_shell(state: dict, shell: VirtualShell, read_input=input, write_output=None, clear_screen=clear_screen) -> None:
    """Run the interactive read-execute loop until exit or interrupt.

    Command output is printed literally so shell text is never interpreted
    as Rich markup. Reading the secret file triggers the USB reward.

    Args:
        state: The current game state.
        shell: Virtual shell executing each input line.
        read_input: Callable reading one line with the prompt.
        write_output: Callable receiving output text. Defaults to the
            module console printer.
        clear_screen: Callable clearing the screen on ``clear``.

    Returns:
        None. Terminates on ``exit`` or on EOF/KeyboardInterrupt.
    """
    write_output = write_output or console.print
    while True:
        try:
            raw = read_input(_prompt_text(shell))
        except (EOFError, KeyboardInterrupt):
            write_output("")
            break
        result = shell.execute(raw)
        if result.clear_requested:
            clear_screen()
        if result.output:
            write_output(Text(result.output))
        if SECRET_PATH in result.read_paths:
            _reward(state, write_output)
        if result.exit_requested:
            break


def inspect_computer(state: dict) -> None:
    """Boot the NixOS computer and open the terminal session.

    Pauses the game timer, plays the boot sequence and logo, then runs the
    shell. The timer stays paused for the whole session and resumes when the
    player leaves the terminal.

    Args:
        state: The current game state.

    Returns:
        None.
    """
    state["is_gametime_paused"] = True
    try:
        loader(
            loading_time=1.2,
            label="Booting up the computer...",
            console=console,
            mode="PROGRESS",
            sequence=computer_sequence,
        )
        clear_screen()
        time.sleep(1)
        nixos_logo()
        time.sleep(2)
        clear_screen()
        console.print(
            "Viola! you are half way in! Now explore the file system to see if you find anything interesting. "
            "Type 'help' to list the available commands."
        )
        time.sleep(1)
        console.print("[bold green]NIXOS // teacher-pc[/]")
        console.print("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
        run_shell(state, VirtualShell(FILESYSTEM))
    finally:
        state["is_gametime_paused"] = False
        clear_screen()


def enter_teachers_room_4(state: dict) -> str:
    """Enter Teacher's Room 4; the computer is the only interactable."""

    state["previous_room"] = "teachersroom4"

    clear_screen()
    state["visited"]["teachersroom4"] = True
    console = Console(legacy_windows=False)

    # Display loading state
    loader(label="Loading teachers room...")

    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])
    state["current_room"] = "teachersroom4"

    while True:
        choice = input("> ").strip().lower()

        if choice in ("use computer", "inspect computer", "boot computer", "computer"):
            inspect_computer(state)

        elif choice in ("?", "help"):
            display_menu(console, room_commands)

        elif choice in ("pause", "save"):
            display_save_menu(state)

        elif choice == "map":
            display_map(state)

        elif choice in ("leave", "exit"):
            return "eastcorridor"

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
