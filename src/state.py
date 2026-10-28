from __future__ import annotations

import json
import os
import re

from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from .utils.generate_save_slot import next_save_slot
from .utils.format_timestamp import format_timestamp
from .model import create_save, get_user_saves, get_user_save
from .display import colorize, header, out
from .utils.colors import RED, BRIGHT_GREEN, BRIGHT_RED, DIM, CYAN

from .utils.duration import calculate_duration

_BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_GAME_STATE_PATH = DATA_DIR / "default_state.json"
USER_STATE_PATH = DATA_DIR / "user_state.json"
HELP_COMMANDS_PATH = DATA_DIR / "help_state.json"
SAVE_DIR = DATA_DIR / "saves"

# Ensure target folder exists
USER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
state: dict = {}
help_commands: list = []

def init() -> None:
    global state
    # 1. Initialize USER_STATE_PATH from default template if missing or 0-byte
    if not USER_STATE_PATH.exists() or USER_STATE_PATH.stat().st_size == 0:
        with open(DEFAULT_GAME_STATE_PATH) as df:
            default_state = json.load(df)
        USER_STATE_PATH.write_text(json.dumps(default_state, indent=2))

    # 2. Load actual active state into memory
    if not state:
        state = json.loads(USER_STATE_PATH.read_text())

    if not help_commands:
        help_commands[:] = json.loads(HELP_COMMANDS_PATH.read_text(encoding="utf-8"))
    return None

def auto() -> None:
    start_time = state["game_state"]["timestamp"] or datetime.now(timezone.utc).isoformat()
    current_time = datetime.now(timezone.utc).isoformat()
    duration = calculate_duration(start_time, current_time)
    state["game_state"]["duration"] = str(duration) or "00:00:00"
    with open(USER_STATE_PATH, "w") as a:
        json.dump(state, a, indent=4)

    if state["workbench"]["is_ready"] and state["game_state"]["phase"] == "EXPLORATION":
        state["game_state"]["phase"] = "ASSEMBLY"
        state["game_state"]["phases"]["assembly"]["activated"] = True


def save(details: Any = None) -> None:
    """Persists current runtime state to disk."""
    from .room import render
    if not state["player"].get("id"):
        render(colorize("You have to register to save, go to the front desk", RED))
        return None

    filename = details["target"] if details else None
    if filename is None:
        filename = next_save_slot(state["player"]["name"])

    filename =  re.sub(r"[^\w-]", "", filename.replace(" ", "_"))
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, f"{filename}.json")

    if not os.path.exists(save_path):
        with open(save_path, "w") as s:
            json.dump(state, s, indent=4)
        create_save(filename, state["player"]["id"])
        render(colorize(f"[system] Game saved to {filename}", BRIGHT_GREEN))
        return None
    render(colorize("An unexpected error occurred", BRIGHT_RED))
    return None

def list_saves() -> None:
    width = int(state["terminal_width"])
    header(colorize("SAVED CHECKPOINTS", CYAN))
    user_id = state["player"].get("id")
    out()
    if not user_id:
        text = "You have to register a profile to view saves. Go to the front desk!"
        out(colorize(text.center(width), DIM))
        return None
    user_saves = get_user_saves(user_id)
    if user_saves:
        for row in user_saves:
            date = format_timestamp(row['created_at'])
            space_needed = state["terminal_width"] - len(date) - len(row["slot"])
            print(row["slot"], end=f"{' ' * space_needed}")
            print(colorize(f"{date}", DIM))
        return None

    text = "You currently have no saved slot linked to your profile"
    out(colorize(text.center(width), DIM))
    return None

def spawn() -> str:
    """Guarantee a valid spawn point (default lobby)."""
    room_id = state["player"]["current_room"]
    if not state["game_state"]["timestamp"]:
        state["game_state"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    rooms = state["rooms"]
    player = state["player"]
    current_room = player["current_room"]
    if not isinstance(current_room, str) or current_room not in rooms:
        current_room = room_id if room_id in rooms else next(iter(rooms), "lobby")
    return current_room

def load(details: Any) -> None:
    """Loads a saved game file into active memory."""
    from .room import render
    slot = details["target"].removesuffix(".json")
    if not state["player"].get("id"):
        render(
            colorize(
                text="You have to register to load, go to the front desk",
                color_code=RED
            )
        )
        return None
    is_saved = get_user_save(state["player"]["id"], slot)
    if is_saved is None:
        render(
            colorize(
                text=f"You currently do not have any progress saved as '{slot}'", color_code=RED
                )
            )
        return None
    save_path = SAVE_DIR / f"{slot}.json"
    if not save_path.exists():
        render(colorize(text=f"You currently have no saved progress as '{slot}'", color_code=RED))
        return None

    with open(save_path, encoding="utf-8") as f:
        loaded = json.load(f)
    state.clear()
    state.update(loaded)
    render(colorize(f"Game loaded from {slot}", BRIGHT_GREEN))
    return None

def _history_back() -> None:
    """Move to the previous room in the player's visit history."""
    from .room import render

    player = state["player"]
    history = player.setdefault("move", [])
    if not history:
        render(text=colorize("You have no previous room to go back to.", RED))
        return None

    previous_room = history[-1]
    if previous_room not in state["rooms"]:
        render(text=colorize(f"Unknown destination '{previous_room}'.", RED))
        return None

    history.pop()
    player.setdefault("forward", []).append(player["current_room"])
    player["current_room"] = previous_room
    render()
    return None


def _history_forward() -> None:
    """Move forward again after going back through history."""
    from .room import render

    player = state["player"]
    forward = player.setdefault("forward", [])
    if not forward:
        render(text=colorize("You have no forward room to go to.", RED))
        return None

    next_room = forward[-1]
    if next_room not in state["rooms"]:
        render(text=colorize(f"Unknown destination '{next_room}'.", RED))
        return None

    forward.pop()
    player.setdefault("move", []).append(player["current_room"])
    player["current_room"] = next_room
    render()
    return None


def move(details: Any) -> None:
    """Move by direction, adjacent room, or history ('back'/'forward')."""
    from .parser import ROOM_ALIASES, resolve_room_target
    from .room import render

    destination = details["target"]
    target = resolve_room_target(destination)

    if target == "back":
        return _history_back()
    if target == "forward":
        return _history_forward()

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    exits = room_data["exits"]

    if target in ROOM_ALIASES.values():
        target_id = exits.get(target)
    else:
        target_id = target if target in exits.values() else None

    if not target_id:
        adjacent = ", ".join(sorted(set(exits.values()))) or "nowhere"
        render(text=colorize(text=f"You cannot go to {destination} from here. Adjacent: {adjacent}.", color_code=RED))
        return None

    target_data = state["rooms"].get(target_id)
    if not target_data:
        render(
            text=colorize(
                text=f"Unknown destination '{target_id}'.",
                color_code=RED
                )
            )
        return None

    requires = target_data.get("requires")
    if requires and requires not in state["player"]["inventory"]:
        render(
            text=colorize(
                text=f"The door is locked. Access requires: {requires}.",
                color_code=RED
            )
        )
        return None
    if target_data.get("restricted") and not requires:
        render(
            text=colorize(
                text="The door is locked.",
                color_code=RED
            )
        )
        return None

    state["player"].setdefault("forward", []).clear()
    state["player"]["current_room"] = target_id
    state["player"].setdefault("move", []).append(current_room)
    render()
    return None