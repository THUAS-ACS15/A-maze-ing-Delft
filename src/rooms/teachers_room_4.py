import time

from rich.console import Console

from ..utils.colors import CYAN, BLUE, BOLD, RESET
from ..display import clear
from ..state import state, auto
from ..room import render
from ..utils.shell import VirtualShell
from ..utils.loader import loader
from src.assets.nixos import nixos as nixos_logo


computer_sequence = [
    "systemd-boot → NixOS Generation 42",
    "<<< NixOS Stage 1 >>> loading kernel modules",
    "LUKS unlock… skipped (no secrets here. Probably.)",
    "Mounting /nix/store from /dev/sda1",
    "Stage 2 activation: /etc, users, secrets",
    "starting systemd... (PID 1)",
    "Reached graphical.target",
]

SECRET_PATH = "/home/teacher/.secret/super_secret_file.txt"

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
                    "The Secret Key has been copied to your inventory.\n"
                ),
            },
            ".bashrc": "# ~/.bashrc\nalias ll='ls -l'\n",
            "README.txt": "Welcome to teacher-pc. Type 'help' to see the available commands.\n",
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


def _prompt_text(shell: VirtualShell) -> str:
    top_line = f"{CYAN}┌──({BLUE}{shell.user}㉿{shell.hostname}{CYAN})-[{BOLD}{shell.display_cwd}{RESET}{CYAN}]{RESET}"
    bottom_line = f"{CYAN}└─{BLUE}${RESET} "
    return f"{top_line}\n{bottom_line}"


def _award_secret_key(write_output=console.print) -> None:
    inventory = state["player"]["inventory"]
    state["flags"]["tr4_secret_key_copied"] = True
    if "secret_key" in inventory:
        write_output("[dim]The Secret Key is already in your inventory.[/]")
        return
    inventory.append("secret_key")
    name = state.get("items", {}).get("secret_key", {}).get("name", "Secret Key")
    write_output(f"[bold green]{name} added to your inventory![/]")


def run_shell(shell: VirtualShell, read_input=input, write_output=console.print, clear_screen=clear) -> None:
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
            write_output(result.output)
        if SECRET_PATH in result.read_paths:
            _award_secret_key(write_output)
        if result.exit_requested:
            break


def inspect_computer() -> None:
    state["game_state"]["duration"]["pause"] = True
    try:
        loader(
            loading_time=1.2,
            label="Booting up the computer...",
            console=console,
            mode="PROGRESS",
            sequence=computer_sequence,
        )
        clear()
        time.sleep(1)
        console.print(nixos_logo)
        time.sleep(2)
        clear()
        console.print(
            "Viola! you are half way in! Now explore the file system to see if you find anything interesting."
        )
        time.sleep(1)
        console.print("[bold green]NIXOS // teacher-pc[/]")
        console.print("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
        run_shell(VirtualShell(FILESYSTEM))
    finally:
        auto()
        state["game_state"]["duration"]["pause"] = False
        clear()
        render()
