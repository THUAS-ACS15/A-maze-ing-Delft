# -----------------------------------------------------------------------------
# File: main_menu.py
# Project: A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clear_screen
from rich.console import Console
from rich.align import Align
from rich.text import Text
from src.state import SAVE_DIR

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
▀▀ ▀▀     ▀▀    ▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀▀     ▀▀▀▀ ▀▀  ▀▀ ▀▀▀▀▀       ▀▀▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀▀     ▀▀ 

"""

MENU_OPTIONS = ["CONTINUE", "NEW GAME", "CREDITS", "EXIT"]


def readKey() -> str:
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
        key = msvcrt.getch()

        # Arrow keys are sent as two bytes on Windows: b'\xe0' followed by a direction byte
        if key == b"\xe0":
            direction = msvcrt.getch()
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
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)


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

    def renderMenu() -> None:
        """
        Draws the title and the menu options, highlighting the current selection.

        Inputs: NONE

        Outputs: NONE
        """

        clear_screen()
        console.print(Align.center(GAME_TITLE_ART, vertical="middle"))
        console.print()
        for index, option in enumerate(MENU_OPTIONS):
            if index == selected_index:
                option_text = Text(f"> {option} <", style="bold green")
            else:
                option_text = Text(f"  {option}  ", style="white")
            console.print(Align.center(option_text))

    renderMenu()

    while True:
        key = readKey()

        if key == "up":
            selected_index = (selected_index - 1) % len(MENU_OPTIONS)
            renderMenu()
        elif key == "down":
            selected_index = (selected_index + 1) % len(MENU_OPTIONS)
            renderMenu()
        elif key == "enter":
            return MENU_OPTIONS[selected_index].lower()


def select_save_slot(mode: str) -> int | None:
    """
    Shows the 3 save slots and lets the player pick one with the arrow keys.

    In "continue" mode, picking an empty slot does nothing (there is nothing
    to continue). In "new game" mode, every slot can be picked, even one that
    already has a save (starting a new game there will overwrite it later).
    A "BACK" option is always shown to return to the main menu.

    Inputs:
        - mode (str): "new game" or "continue".

    Outputs:
        - int | None: the chosen slot number (1, 2 or 3), or None if the
          player picked "BACK".
    """

    console = Console()
    options = [1, 2, 3, "back"]
    selected_index = 0

    def slotLabel(slot: int) -> str:
        """Returns a display label for the given slot, showing whether it has a save."""

        save_path = SAVE_DIR / f"save_slot_{slot}.json"
        if save_path.exists():
            return f"Slot {slot} - Saved game"
        return f"Slot {slot} - Empty"

    def renderSlots() -> None:
        """Draws the slot-selection screen, highlighting the current selection."""

        clear_screen()
        title = "NEW GAME" if mode == "new game" else "CONTINUE"
        console.print(Align.center(title))
        console.print()
        for index, option in enumerate(options):
            label = "BACK" if option == "back" else slotLabel(option)
            if index == selected_index:
                option_text = Text(f"> {label} <", style="bold green")
            else:
                option_text = Text(f"  {label}  ", style="white")
            console.print(Align.center(option_text))

    renderSlots()

    while True:
        key = readKey()

        if key == "up":
            selected_index = (selected_index - 1) % len(options)
            renderSlots()
        elif key == "down":
            selected_index = (selected_index + 1) % len(options)
            renderSlots()
        elif key == "enter":
            chosen = options[selected_index]

            if chosen == "back":
                return None

            if mode == "continue":
                save_path = SAVE_DIR / f"save_slot_{chosen}.json"
                if not save_path.exists():
                    # Nothing to continue in an empty slot, stay on this screen.
                    continue

            return chosen