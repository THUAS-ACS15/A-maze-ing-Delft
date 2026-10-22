from __future__ import annotations

import json
import os
from datetime import timezone, datetime
from pathlib import Path

from .display import colorize
from .utils.colors import RED

from .utils.duration import calculate_duration

_BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GAME_STATE_PATH = _BASE_DIR / "data" / "game_state.json"
USER_STATE_PATH = _BASE_DIR / "data" / "user_state.json"
HELP_COMMANDS_PATH = _BASE_DIR / "data" / "help_state.json"
SAVE_DIR = _BASE_DIR / "saves"

# Ensure target folder exists
USER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
state: dict = {}
help_commands: list = []

def initialize() -> None:
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
    return None

def auto() -> None:
    duration = calculate_duration(state["game_state"]["timestamp"], datetime.now(timezone.utc).isoformat())
    state["game_state"]["duration"] = str(duration) or "00:00:00"
    with open(USER_STATE_PATH, "w") as a:
        json.dump(state, a, indent=4)

    if state["workbench"]["is_ready"] and state["game_state"]["phase"] == "EXPLORATION":
        state["game_state"]["phase"] = "ASSEMBLY"
        state["game_state"]["phases"]["assembly"]["activated"] = True

def save(filename: str = "save_slot_1.json") -> tuple[bool, str]:
    """Persists current runtime state to disk."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, filename)

    with open(save_path, "w", encoding="utf-8") as s:
        json.dump(state, s, indent=4)
    return True, f"[System] Game saved to {save_path}"

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


def load(filename: str = "save_slot_1.json") -> bool:
    """Loads a saved game file into active memory."""
    global state
    save_path = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(save_path):
        print("[System] No save file found.")
        return False

    with open(save_path, encoding="utf-8") as f:
        state = json.load(f)
    print(f"[System] Loaded saved file from {save_path}")
    return True

def move(destination: str) -> None:
    """Move by direction ('north'/'n') or adjacent room id/name.

    Adjacent-only: a room name is accepted only if it appears in the
    current room's exits values. Returns (ok, next_room_id or message).
    """
    from .parser import ROOM_ALIASES, resolve_room_target
    from .room import render

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    exits = room_data["exits"]

    target = resolve_room_target(destination)
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

    state["player"]["current_room"] = target_id
    state["player"]["move"].append(current_room)
    render()
    return None