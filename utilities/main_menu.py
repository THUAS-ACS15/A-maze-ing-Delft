# -----------------------------------------------------------------------------
# File: main_menu.py
# Project: A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

import readchar  # type: ignore[import-not-found, import-untyped]
from utilities.clear_screen import clear_screen
from utilities.status_bar import display_top_bar
from rich.console import Console
from rich.align import Align
from rich.text import Text

# Cross-platform single key reading via readchar.

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

    Backend is readchar (cross-platform). Arrow key presses are
    translated into "up" or "down"; Enter is translated into
    "enter". Any other key returns an empty string.

    Inputs: NONE

    Outputs:
        - str: "up", "down", "enter" or "" for any other key.
    """
    try:
        key = readchar.readkey()
    except Exception:
        return ""
    if key in (readchar.key.UP, "\x1b[A"):
        return "up"
    if key in (readchar.key.DOWN, "\x1b[B"):
        return "down"
    if key in (readchar.key.ENTER, "\r", "\n"):
        return "enter"
    return ""

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
        console.print(Align.center("[italic][bold gray]use arrow keys to navigate, enter to select[/bold gray][/italic]")) #noqa: E501
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