# -----------------------------------------------------------------------------
# File: credits.py
# Project: A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

from time import sleep
from utilities.clear_screen import clear_screen
from utilities.status_bar import display_top_bar
from rich.console import Console
from rich.align import Align

CREDITS_LINES = [
    "A-MAZE-ING DELFT",
    "",
    "PROGRAMMING & GAME DEVELOPERS",
    "Sadanand Pandit",
    "Leon Stanciu",
    "João Silva",
    "Gift Odigwe",
    "Dominik Knapek",
    "",
    "LECTURERS",
    "Aram Rostamnejad Khatir",
    "Glenn Abraas",
    "Wesley van der Velde",
    "Renee Tentori",
    "Sam van Buuren",
    "",
    "Made with Python",
    "",
    "ACS Q1 - The Hague University of Applied Sciences, Delft, 2026",
    "",
    "Thanks for playing!"
]


def display_credits() -> None:
    """
    Shows the game credits, scrolling slowly up the screen line by line.

    This function prints the CREDITS_LINES list one line at a time, with a
    short pause between each, giving a slow scrolling effect similar to the
    end credits of a game. The player can skip the credits at any point by
    pressing Enter.

    Inputs: NONE

    Outputs: NONE
    """
    console = Console()
    clear_screen("", False)
    display_top_bar(console)

    for line in CREDITS_LINES:
        if line == "":
            console.print("\n")
        console.print(Align.center(line))
        sleep(0.4)

    # Escape the brackets so Rich displays the message instead of treating it as markup.
    console.print(Align.center("\\[press enter to go back]"))
    input()