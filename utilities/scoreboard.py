# -----------------------------------------------------------------------------
# File: scoreboard.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------
import sqlite3
import msvcrt

from rich.align import Align
from rich.console import Console, Group
from rich.table import Table


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

def show_scoreboard() -> None:
    """
    Displays the scoreboard on the screen, in increments of 10 entries.

    The  
    """
    recreate_scoreboard_table()
    entries = get_scoreboard_entries()

    console = Console()
    page = 0
    page_count = max(1, (len(entries) + 9) // 10)

    def _read_key() -> str | bytes:
        '''Read input continuously from keyboard so scroll left-right is possible.'''
        import os
        import sys

        # If on windows, msvcrt can continously capture input automatically
        # so we can just check if the char is a two-byte sequence
        # the second char K is for < and M is for >
        if os.name == "nt":
            win_key = msvcrt.getch()
            if win_key in (b"\x00", b"\xe0"):
                char = msvcrt.getch()
                if char == b"K":
                    return "<"
                elif char == b"M":
                    return ">"
                else:
                    return ""
            return win_key.decode(errors = "ignore")

        # MacOS / Linux imports termios to get continuous input
        # set terminal to one-char-at-a-time mode, read one char
        # when stopped, restore initial settings of stdin
        else:
            import termios
            import tty
            stdin = sys.stdin.fileno()
            get_attributes = termios.tcgetattr  # type: ignore[attr-defined]
            set_attributes = termios.tcsetattr  # type: ignore[attr-defined]
            drain = termios.TCSADRAIN  # type: ignore[attr-defined]
            set_cbreak = tty.setcbreak  # type: ignore[attr-defined]
            settings = get_attributes(stdin)
            try:
                set_cbreak(stdin)
                posix_key: str = sys.stdin.read(1)
                # if it starts with an escape char, check last 2 if they're C or D for left/right arrow keys
                if posix_key == "\x1b":
                    sequence = sys.stdin.read(2)
                    if sequence == "[D":
                        return "<"
                    elif sequence == "[C":
                        return ">"
                    else:
                        return posix_key
            finally:
                set_attributes(stdin, drain, settings)
        return ""

    while True:
        table = Table(title = "Ordered by time played.\n\n\n\n")

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
        console.print(
            Align.center(
                Group(
                    Align.center(SCOREBOARD_TITLE_ART),
                    Align.center(table),
                    "\n\n\n",
                    Align.center(f"< Back | Page {page + 1}/{page_count}, use q to go back | Next >"),
                ),
                vertical = "middle",
            )
        )

        key = _read_key().lower()
        if key == "q":
            break
        if key in ("<", "a"):
            page = max(0, page - 1)
        elif key in (">", "d"):
            page = min(page_count - 1, page + 1)