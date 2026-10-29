# -----------------------------------------------------------------------------
# File: scoreboard.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------
"""Local scoreboard storage and display."""

import sqlite3

from rich.align import Align
from rich.console import Console, Group
from rich.table import Table

from utilities.main_menu import read_key
from utilities.status_bar import display_top_bar

SCOREBOARD_TITLE_ART: str = """
██▀██ ██▀██ ██▀██ ██▀██ ██▀██ ██▀█▄ ██▀██ ██▀██ ██▀██ ██▀█▄
██▄▄▄ ██    ██ ██ ██▄█▀ ██▄   ██▄█▀ ██ ██ ██▄██ ██▄█▀ ██ ██
▄▄ █▓ █▓░▄▄ █▓░█▓ █▓░█▓ █▓░▄▄ █▓ █▓ █▓░█▓ █▓░█▓ █▓░█▓ █▓░█▓
▀▀▀▀▀ ▀▀▀▀▀ ▀▀▀▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀  ▀▀▀▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀▀▀ """

SCOREBOARD_DB_STRUCTURE = """
CREATE TABLE IF NOT EXISTS scoreboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    exploration_percent REAL NOT NULL,
    time_elapsed REAL NOT NULL
);
"""

def _format_time_played(time: float) -> str:
    """Format seconds as 'Xs', 'Ym Zs', or 'Xh Ym Zs'."""
    time = max(time, 0)
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
    Fetches all entries from the scoreboard table, sorted by exploration percentage
    descending and time elapsed ascending.
    """
    with sqlite3.connect("scoreboard.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT player_name, exploration_percent, time_elapsed "
            "FROM scoreboard ORDER BY exploration_percent DESC, time_elapsed ASC"
        )
        return cursor.fetchall()

def add_scoreboard_entry(player_name: str, exploration_percent: float, time_elapsed: float) -> None:
    """Adds a new entry to the scoreboard database.

    This function inserts a new entry into the scoreboard database with the
    provided player name, exploration percentage, and time elapsed.

    Args:
        player_name: The name of the player.
        exploration_percent: The percentage of the map explored by the player.
        time_elapsed: The time elapsed during the game in seconds.
    """
    with sqlite3.connect("scoreboard.db") as db:
        cursor = db.cursor()
        cursor.execute("INSERT OR REPLACE INTO scoreboard \
                       (player_name, exploration_percent, time_elapsed) VALUES \
                       (?, ?, ?)", 
        (player_name, exploration_percent, time_elapsed))
        db.commit()

def display_scoreboard() -> None:
    """Displays the scoreboard on the screen, in increments of 10 entries.

    The scoreboard is displayed in a table format, with the player's name and time elapsed.
    The player can navigate through the pages using the arrow keys for prev/next page.
    Pressing 'enter' will exit and return to main menu.
    """
    recreate_scoreboard_table()
    entries = get_scoreboard_entries()

    console = Console()
    page = 0
    page_count = max(1, (len(entries) + 9) // 10)

    while True:
        table = Table(title = "ordered by exploration percent, then time played\n\n\n\n", width = 80)

        # If entries exist display them from start
        if len(entries) > 0:
            table.add_column(Align.center("Place"), width=5)
            table.add_column(Align.center("Player name"), width=20)
            table.add_column(Align.center("Explored %"), width=20)
            table.add_column(Align.center("Time elapsed"), width=20)

            start = page * 10
            for place, entry in enumerate(entries[start:start + 10], start=start + 1):
                # Get special style if #1 to #3
                style = {1: "bold yellow", 2: "bold white", 3: "bold red"}.get(place)
                table.add_row(
                    str(place),
                    entry[0],
                    f"{entry[1]}%",
                    _format_time_played(entry[2]),
                    style=style,
                )
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
                    Align.center(f"^ previous page | {page + 1}/{page_count} use enter to go back | next v"),
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
