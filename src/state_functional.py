from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


_BASE_DIR = Path(__file__).resolve().parent
GAME_STATE_PATH = _BASE_DIR / "data" / "game_state.json"
USER_STATE_PATH = _BASE_DIR / "data" / "user_state.json"
SAVE_DIR = _BASE_DIR / "saves"

with open(GAME_STATE_PATH, "r") as f:
    state = json.load(f)

with open(USER_STATE_PATH, "r") as u:
    user = json.load(u)

def get_state(key: str | None = None, default: Any = None) -> Any:
    if key is None:
        return state
    return state.setdefault(key, default)

def set_state(key: str, value: Any = None) -> Any:
    if value is None:
        return get_state(key)
    state[key] = value
    return value


def get_default_state(field: str) -> Any:
    with open(GAME_STATE_PATH, "r") as s:
        return json.load(s).get(field, [])

def load_default_state() -> None:
        """Loads a fresh instance from the master game_state.json data template."""
        global state
        with open(GAME_STATE_PATH, encoding="utf-8") as s:
            state = json.load(s)

def load_user_state() -> None:
    """Loads a fresh instance from the master user_state.json data template."""
    global user
    with open(USER_STATE_PATH, encoding="utf-8") as u:
        user = json.load(u)

def is_running() -> bool:
    return bool(get_state('running', True))

def get_phase() -> str:
    phase = state.get('phase', state.get('game_phase', 'EXPLORATION'))
    return phase if isinstance(phase, str) else 'EXPLORATION'

def get_current_room_id() -> str:
    room = state.get("player", {}).get("current_room", "lobby")
    if isinstance(room, str) and room in state.get("rooms", {}):
        return room
    return "lobby"

def save_to_file(filename: str = "save_slot_1.json") -> None:
    """Persists current runtime state to disk."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, filename)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    print(f"[System] Game saved to {save_path}")

def spawn( room_id: str = "lobby") -> str:
    """Guarantee a valid spawn point (default lobby)."""
    rooms = state.get("rooms", {})
    player = state.setdefault("player", {})
    current = player.get("current_room")
    if not isinstance(current, str) or current not in rooms:
        player["current_room"] = room_id if room_id in rooms else next(iter(rooms), "lobby")
    return player["current_room"]

def get_room_data(room_id: str) -> dict[str, Any]:
    rooms = state.get("rooms", {})
    if isinstance(rooms, dict):
        data = rooms.get(room_id, {})
        if isinstance(data, dict):
            return data
    return {}

def get_inventory() -> list[str]:
    player = state.setdefault("player", {})
    if not isinstance(player, dict):
        state["player"] = player = {}
    inv = player.setdefault("inventory", [])
    return inv if isinstance(inv, list) else []

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
    from .parser_functional import ROOM_ALIASES, resolve_room_target

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
    if requires and requires not in get_inventory():
        return False, f"The door is locked. Access requires: {requires}."
    if target_data.get("restricted") and not requires:
        return False, "The door is locked."

    state["player"]["current_room"] = target_id
    state["player"]["move"].append(current_room)
    return True, target_id