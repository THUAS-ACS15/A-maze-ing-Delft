from __future__ import annotations

import json
import os
from datetime import timezone, datetime
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GAME_STATE_PATH = _BASE_DIR / "data" / "game_state.json"
USER_STATE_PATH = _BASE_DIR / "data" / "user_state.json"
SAVE_DIR = _BASE_DIR / "saves"

with open(USER_STATE_PATH, "r") as u:
    user = json.load(u)

with open(DEFAULT_GAME_STATE_PATH, "r") as f:
    state = json.load(f)

state.update(user)

with open(USER_STATE_PATH, "w") as f:
    json.dump(state, f, indent=4)

def auto_save() -> None:
    with open(USER_STATE_PATH, "w") as a:
        json.dump(state, a, indent=4)

def save_to_file(filename: str = "save_slot_1.json") -> tuple[bool, str]:
    """Persists current runtime state to disk."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, filename)

    with open(save_path, "w", encoding="utf-8") as s:
        json.dump(state, s, indent=4)
    return True, f"[System] Game saved to {save_path}"

def spawn( room_id: str = "lobby") -> str:
    """Guarantee a valid spawn point (default lobby)."""
    if not state["game_state"]["timestamp"]:
        state["game_state"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    rooms = state["rooms"]
    player = state["player"]
    current_room = player["current_room"]
    if not isinstance(current_room, str) or current_room not in rooms:
        current_room = room_id if room_id in rooms else next(iter(rooms), "lobby")
    return current_room


def load_from_file(filename: str = "save_slot_1.json") -> bool:
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

def move_player(destination: str) -> tuple[bool, str]:
    """Move by direction ('north'/'n') or adjacent room id/name.

    Adjacent-only: a room name is accepted only if it appears in the
    current room's exits values. Returns (ok, next_room_id or message).
    """
    from .parser import ROOM_ALIASES, resolve_room_target

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
        return False, f"You cannot go to {destination} from here. Adjacent: {adjacent}."

    target_data = state["rooms"].get(target_id)
    if not target_data:
        return False, f"Unknown destination '{target_id}'."

    requires = target_data.get("requires")
    if requires and requires not in state["player"]["inventory"]:
        return False, f"The door is locked. Access requires: {requires}."
    if target_data.get("restricted") and not requires:
        return False, "The door is locked."

    state["player"]["current_room"] = target_id
    state["player"]["move"].append(current_room)
    return True, target_id