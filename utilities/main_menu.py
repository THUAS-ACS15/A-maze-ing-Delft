# -----------------------------------------------------------------------------
# File: main_menu.py
# Project: A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clear_screen
from utilities.status_bar import display_top_bar
from rich.console import Console
from rich.align import Align
from rich.text import Text

# Cross-platform single key reading: msvcrt exists only on Windows,
# termios/tty are used instead on macOS/Linux.
try:
    import msvcrt
    IS_WINDOWS = True
except ImportError:
    import termios
    import tty
    IS_WINDOWS = False

# ASCII Font is Blunder
GAME_TITLE_ART: str = """
██▀██     ██▀██▀██ ██▀██ ██▀██ ██▀██     ▀██▀ ███▄██ ██▀██       ██▀█▄ ██▀██ ██    ██▀██ ▀██▀
██▄██ ███ ██ ██ ██ ██▄██ ▄▄▄██ ██▄   ███  ██  ██ ▀██ ██ ▀▀       ██ ██ ██▄   ██    ██▄    ██ 
█▓░█▓     █▓░█▓░█▓ █▓░█▓ ▓█ ▄▄ █▓░▄▄      █▓░ █▓░ █▓ █▓░██▀      █▓░█▓ █▓░▄▄ █▓░▄▄ █▓░    █▓░
▀▀ ▀▀     ▀▀    ▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀▀     ▀▀▀▀ ▀▀  ▀▀ ▀▀▀▀▀       ▀▀▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀▀     ▀▀ """

MENU_OPTIONS = ["CONTINUE", "NEW GAME", "CREDITS", "SCOREBOARD", "EXIT"]


def read_key() -> str:
    """
    Reads a single keypress from the terminal, without needing Enter.

    Works on Windows (msvcrt) and on macOS/Linux (termios/tty). Arrow key
    presses are translated into "up" or "down"; Enter is translated into
    "enter". Any other key returns an empty string.

    Inputs: NONE

    Outputs:
        - str: "up", "down", "enter" or "" for any other key.
    """

    if IS_WINDOWS:
        key = msvcrt.getch()  # type: ignore[attr-defined]

        # Arrow keys are sent as two bytes on Windows: b'\xe0' followed by a direction byte
        if key == b"\xe0":
            direction = msvcrt.getch()  # type: ignore[attr-defined]
            if direction == b"H":
                return "up"
            elif direction == b"P":
                return "down"
            return ""
        elif key in (b"\r", b"\n"):
            return "enter"
        return ""

    else:
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            key = sys.stdin.read(1)

            # Arrow keys are sent as an escape sequence on macOS/Linux: '\x1b[A' (up), '\x1b[B' (down)
            if key == "\x1b":
                key += sys.stdin.read(2)
                if key == "\x1b[A":
                    return "up"
                elif key == "\x1b[B":
                    return "down"
                return ""
            elif key in ("\r", "\n"):
                return "enter"
            return ""
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings) # ignore [attr-defined]

def display_main_menu() -> str:
    """
    Displays the main menu and lets the player pick an option with the arrow keys.

    This function shows the game title and the list of menu options (CONTINUE,
    NEW GAME, CREDITS, EXIT). The player moves the selection up and down with
    the Up/Down arrow keys and confirms a choice with Enter.

    Inputs: NONE

    Outputs:
        - str: the chosen option in lowercase ("continue", "new game", "credits" or "exit")
    """

    console = Console()
    selected_index = 0

    def render_menu() -> None:
        """
        Draws the title and the menu options, highlighting the current selection.

        Inputs: NONE

        Outputs: NONE
        """

        clear_screen("", run_status_bar_update=False)
        display_top_bar(console)
        console.print(Align.center(GAME_TITLE_ART, vertical="middle"))
        console.print(Align.center("[italic][bold gray]use arrow keys to navigate, enter to select[/bold gray][/italic]"))
        console.print('\n\n\n')
        for index, option in enumerate(MENU_OPTIONS):
            if index == selected_index:
                option_text = Text(f"> {option} <\n", style="bold green")
            else:
                option_text = Text(f"  {option}  \n", style="white")
            console.print(Align.center(option_text))

    render_menu()

    while True:
        key = read_key()

        if key == "up":
            selected_index = (selected_index - 1) % len(MENU_OPTIONS)
            render_menu()
        elif key == "down":
            selected_index = (selected_index + 1) % len(MENU_OPTIONS)
            render_menu()
        elif key == "enter":
            return MENU_OPTIONS[selected_index].lower()