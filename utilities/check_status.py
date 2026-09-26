# -----------------------------------------------------------------------------
# File: check_status.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe
# -----------------------------------------------------------------------------

import os
import time

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

# Consistent text style
HEADER_STYLE = "bold green"

def _show_line(console: Console, text: str, style: str, delay: float) -> None:
    """Print one styled line, pausing briefly to keep the streaming feel."""
    console.print(Text(text, style=style or ""))
    if delay > 0:
        time.sleep(delay * 10)


def _format_time_played(start_time) -> str:
    """Format elapsed seconds since start_time as 'Xs' / 'Ym Zs' / 'Xh Ym Zs'."""
    import math

    try:
        elapsed = math.ceil(time.time() - float(start_time))
    except (TypeError, ValueError):
        return "Unknown"
    if elapsed < 0:
        elapsed = 0
    if elapsed > 3600:
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours}h {minutes}m {seconds}s"
    if elapsed > 60:
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes}m {seconds}s"
    return f"{elapsed}s"


def check_status(state: dict, loading_time: float = 1.2, stream_delay: float = 0.015, pause: bool = False) -> None:
    """
    Display the player's overall status with loading + streaming effect.

    Inputs:
        - state (dict): game state with visited/completed/coin_balance/student_id_obtained/inventory/current_room/previous_room/start_time
        - loading_time (float): seconds for the loading spinner (0 skips it, for tests)
        - stream_delay (float): pause between lines (0 = instant, for tests)
        - pause (bool): if True, wait for Enter at the end so clearScreen() doesn't wipe output

    Outputs: NONE (but shifts state["start_time"] forward by the time the
        status screen was open, pausing game time while viewing status)
    """
    enter_time = time.time()
    try:
        console = Console(legacy_windows=False)

        # 1. Loading state
        if loading_time > 0:
            if os.getenv("PYCHARM_HOSTED"):
                print("Fetching player status...")
                time.sleep(loading_time)
            else:
                with console.status("[bold cyan]Fetching player status...[/]", spinner="dots"):
                    time.sleep(loading_time)

        # 2. Gather data (tolerant of missing keys)
        visited = state.get("visited", {})
        completed = state.get("completed", {})
        coin_balance = state.get("coin_balance", 0)
        has_id = state.get("student_id_obtained", False)
        inventory = state.get("inventory", [])
        current_room = state.get("current_room", "Unknown")
        previous_room = state.get("previous_room", "Unknown")
        start_time = state.get("start_time", None)
        time_played_str = _format_time_played(start_time) if start_time is not None else "Unknown"

        explored = [k for k, v in visited.items() if v]
        unexplored = [k for k, v in visited.items() if not v]
        completed_rooms = [k for k, v in completed.items() if v]
        total_rooms = len(visited)
        explored_percent = round((len(explored) / total_rooms) * 100, 2) if total_rooms > 0 else 0.0

        explored_str = "[" + ", ".join(explored) + "]" if explored else "(none yet)"
        unexplored_str = "[" + ", ".join(unexplored) + "]" if unexplored else "(all rooms visited!)"
        completed_str = "[" + ", ".join(completed_rooms) + "]" if completed_rooms else "(none yet)"
        inventory_str = "[" + ", ".join(inventory) + "]" if inventory else "Empty"
        id_str = "Yes" if has_id else "No - visit the Front Desk"
        console.print()

        _show_line(console, f"Current room: {current_room}", HEADER_STYLE, stream_delay)
        _show_line(console, f"Previous room: {previous_room}", HEADER_STYLE, stream_delay)
        _show_line(console, f"Time played: {time_played_str}", HEADER_STYLE, stream_delay)
        console.print()

        _show_line(console, f"Rooms Explored ({len(explored)}/{total_rooms} - {explored_percent}%):", HEADER_STYLE, stream_delay)
        _show_line(console, explored_str, "", stream_delay)
        console.print()

        _show_line(console, f"Not yet explored ({len(unexplored)}):", HEADER_STYLE, stream_delay)
        _show_line(console, unexplored_str, "", stream_delay)
        console.print()

        _show_line(console, f"Challenges completed ({len(completed_rooms)}):", HEADER_STYLE, stream_delay)
        _show_line(console, completed_str, "", stream_delay)
        console.print()

        _show_line(console, f"Coin balance: {coin_balance}", HEADER_STYLE, stream_delay)
        _show_line(console, f"Student ID: {id_str}", HEADER_STYLE, stream_delay)
        console.print()

        _show_line(console, f"Inventory ({len(inventory)}):", HEADER_STYLE, stream_delay)
        _show_line(console, inventory_str, "", stream_delay)

        if pause:
            from utilities.inventory_viewer import item_descriptions

            console.print("Available commands:")
            console.print("- inventory : View item details")
            console.print(f"- exit      : Back to {current_room}")
            while Prompt.ask(
                "Command",
                choices=["inventory", "exit"],
                default="exit",
                show_choices=True,
                console=console,
            ) == "inventory":
                if not inventory:
                    console.print("No inventory.")
                else:
                    for item in inventory:
                        console.print(f"[bold]{item}[/]: {item_descriptions.get(item, 'No description yet.')}")
    finally:
        # Exclude the whole status screen duration from game time.
        start_time = state.get("start_time", None)
        if isinstance(start_time, (int, float)) and not isinstance(start_time, bool):
            state["start_time"] = start_time + (time.time() - enter_time)


# Alias preserving the original camelCase name used across rooms.
checkStatus = check_status
