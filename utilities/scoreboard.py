# -----------------------------------------------------------------------------
# File: scoreboard.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------
import sqlite3

from rich.align import Align
from rich.console import Console, Group
from rich.table import Table

from utilities.status_bar import display_top_bar
from utilities.main_menu import read_key

SCOREBOARD_TITLE_ART: str = """
██▀██ ██▀██ ██▀██ ██▀██ ██▀██ ██▀█▄ ██▀██ ██▀██ ██▀██ ██▀█▄
██▄▄▄ ██    ██ ██ ██▄█▀ ██▄   ██▄█▀ ██ ██ ██▄██ ██▄█▀ ██ ██
▄▄ █▓ █▓░▄▄ █▓░█▓ █▓░█▓ █▓░▄▄ █▓ █▓ █▓░█▓ █▓░█▓ █▓░█▓ █▓░█▓
▀▀▀▀▀ ▀▀▀▀▀ ▀▀▀▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀  ▀▀▀▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀▀▀ """

SCOREBOARD_DB_STRUCTURE = """
CREATE TABLE IF NOT EXISTS scoreboard (
    player_name TEXT PRIMARY KEY NOT NULL,
    time_elapsed REAL NOT NULL
);
"""

def _format_time_played(time: float) -> str:
    if time < 0:
        time = 0
    if time > 3600:
        hours = time // 3600
        minutes = (time % 3600) // 60
        seconds = round(time % 60, 2)
        return f"{int(hours)}h {int(minutes)}m {seconds}s"
    if time > 60:
        minutes = round(time // 60, 0)
        seconds = round(time % 60, 2)
        return f"{int(minutes)}m {seconds}s"
    return f"{time}s"

def recreate_scoreboard_table() -> None:
    """Recreates the database 'saves' table."""
    with sqlite3.connect("scoreboard.db") as db:
        cursor = db.cursor()
        cursor.executescript(SCOREBOARD_DB_STRUCTURE)
        db.commit()

def get_scoreboard_entries() -> list[tuple]:
    """
    Fetches all entries from the scoreboard table, sorted by time elapsed in ascending order.
    """
    with sqlite3.connect("scoreboard.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT player_name, time_elapsed FROM scoreboard ORDER BY time_elapsed ASC")
        return cursor.fetchall()

def add_scoreboard_entry(player_name: str, time_elapsed: float) -> None:
    with sqlite3.connect("scoreboard.db") as db:
        cursor = db.cursor()
        cursor.execute("INSERT OR REPLACE INTO scoreboard (player_name, time_elapsed) VALUES (?, ?)", 
        (player_name, time_elapsed))
        db.commit()

def display_scoreboard() -> None:
    """
    Displays the scoreboard on the screen, in increments of 10 entries.

    The scoreboard is displayed in a table format, with the player's name and time elapsed. 
    The player can navigate through the pages using the arrow keys for prev/next page.
    Pressing 'enter' will exit and return to main menu.
    
    Inputs: NONE

    Outputs: NONE
    """
    recreate_scoreboard_table()
    entries = get_scoreboard_entries()

    console = Console()
    page = 0
    page_count = max(1, (len(entries) + 9) // 10)

    while True:
        table = Table(title = "ordered by time played (lowest to highest)\n\n\n\n", width = 50)

        # If entries exist display them from start
        if len(entries) > 0:
            table.add_column("Place", justify="right", width=5)
            table.add_column(Align.center("Player name"), width=20)
            table.add_column(Align.center("Time elapsed"), width=20)

            start = page * 10
            for place, entry in enumerate(entries[start:start + 10], start=start + 1):
                # Get special style if #1 to #3
                style = {1: "bold yellow", 2: "bold white", 3: "bold red"}.get(place)
                table.add_row(str(place), entry[0], _format_time_played(entry[1]), style=style)
        else:
            table.add_column(Align.center("No entries yet."), width = 20)

        console.clear()
        display_top_bar(console)
        console.print(
            Align.center(
                Group(
                    Align.center(SCOREBOARD_TITLE_ART),
                    Align.center(table),
                    "\n\n\n",
                    Align.center(f"^ Previous | Page {page + 1}/{page_count}, use enter to go back | Next v"),
                ),
                vertical = "middle",
            )
        )

        key = read_key().lower()
        if key == "enter":
            break
        if key == "up":
            page = max(0, page - 1)
        elif key == "down":
            page = min(page_count - 1, page + 1)