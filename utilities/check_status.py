# -----------------------------------------------------------------------------
# File: check_status.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe
# -----------------------------------------------------------------------------
import time

from rich.console import Console
from rich.prompt import Prompt

from utilities.clear_screen import clear_screen
from utilities.loader import loader
from utilities.print_helpers import print_line

# Consistent text style
HEADER_STYLE = "bold green"

# Consistent delay
DELAY=0.0025

def _format_time_played(start_time: float, time_elapsed: float) -> str:
    """Format elapsed seconds since start_time as 'Xs' / 'Ym Zs' / 'Xh Ym Zs'."""
    import math

    try:
        elapsed = math.ceil(time.time() - float(start_time) + float(time_elapsed))
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

def check_status(
    state: dict,
    loading_time: float = 1.2,
    stream_delay: float = 0.015,
    pause: bool = True,
) -> None:
    """
    Display the player's overall status with loading + streaming effect.

    Inputs:
        - state (dict): game state with visited/completed/coin_balance/student_id_obtained/
        inventory/current_room/previous_room/start_time
        - loading_time (float): seconds for the loading spinner (0 skips it, for tests)
        - stream_delay (float): pause between lines (0 = instant, for tests)
        - pause (bool): if True, wait for Enter at the end so clearScreen() doesn't wipe output

    Outputs: NONE (but shifts state["start_time"] forward by the time the
        status screen was open, pausing game time while viewing status)
    """
    enter_time = time.time()
    state["is_gametime_paused"] = True
    try:
        console = Console(legacy_windows=False)
        clear_screen()
        
        # 1. Loading state
        if loading_time > 0:
            loader(
                loading_time,
                label="Fetching your current status...",
            )

        # 2. Gather data (tolerant of missing keys)
        completed = state.get("completed", {})
        coin_balance = state.get("coin_balance", 0)
        has_id = state.get("student_id_obtained", False)
        inventory = state.get("inventory", [])
        current_room = state.get("current_room", "Unknown")
        previous_room = state.get("previous_room", "Unknown")
        start_time = state.get("start_time", None)
        time_elapsed = state.get("time_elapsed", 0.0)
        time_played_str = (
            _format_time_played(start_time, time_elapsed)
            if start_time is not None
            else "Unknown"
        )

        explored = [k for k, v in completed.items() if v]
        unexplored = [k for k, v in completed.items() if not v]
        completed_rooms = [k for k, v in completed.items() if v]
        total_rooms = len(completed)
        explored_percent = (
            round(
                (len(explored) / total_rooms) * 100,
                2,
            )
            if total_rooms > 0
            else 0.0
        )

        explored_str = "[" + ", ".join(explored) + "]" if explored else "(none yet)"
        unexplored_str = "[" + ", ".join(unexplored) + "]" if unexplored else "(all rooms visited!)"
        completed_str = "[" + ", ".join(completed_rooms) + "]" if completed_rooms else "(none yet)"
        inventory_str = "[" + ", ".join(inventory) + "]" if inventory else "Empty"
        id_str = "Yes" if has_id else "No - visit the Front Desk"
        console.print()

        print_line(
            text=f"Current room: {current_room}",
            delay=DELAY

        )
        print_line(
            text=f"Previous room: {previous_room}",
            delay=DELAY
        )
        print_line(
            text=f"Time played: {time_played_str}",
            delay=DELAY
        )
        console.print()

        print_line(
            text=f"Rooms Explored ({len(explored)}/{total_rooms} - {explored_percent}%):",
            delay=DELAY
        )
        print_line(text=explored_str, delay=DELAY)
        console.print()

        print_line(
            text=f"Not yet explored ({len(unexplored)}):",
            delay=DELAY
        )
        print_line(unexplored_str, delay=DELAY)
        console.print()

        print_line(
            f"Challenges completed ({len(completed_rooms)}):",
            delay=DELAY
        )
        print_line(text=completed_str, delay=DELAY)
        console.print()

        print_line(
            text=f"Coin balance: {coin_balance}",
            delay=DELAY
        )
        print_line(
            text=f"Student ID: {id_str}",
            delay=DELAY
        )
        console.print()

        print_line(
            text=f"Inventory ({len(inventory)}):",
            delay=DELAY
        )
        print_line(text=inventory_str, delay=DELAY)

        if pause:
            from utilities.inventory_viewer import (
                item_descriptions,
            )

            print_line("\n \n Available commands:")
            choices = ["exit"]
            if inventory:
                console.print("- inventory : View item details")
                choices = ["inventory", "exit"]
            console.print(f"- exit      : Back to {current_room}")
            while (
                Prompt.ask(
                    "Command",
                    choices=choices,
                    default="exit",
                    show_choices=True,
                    console=console,
                )
                == "inventory"
            ):
                for item in inventory:
                    print_line(f"[bold]{item}[/]: {item_descriptions.get(item, 'No description yet.')}")
    finally:
        # Exclude the whole status screen duration from game time.
        start_time = state.get("start_time", None)
        if isinstance(start_time, (int, float)) and not isinstance(start_time, bool):
            state["start_time"] = start_time + (time.time() - enter_time)
        state["is_gametime_paused"] = False
        clear_screen()
