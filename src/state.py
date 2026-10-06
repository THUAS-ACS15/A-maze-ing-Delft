from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_BASE_DIR = Path(__file__).resolve().parent
GAME_STATE_PATH = _BASE_DIR / "data" / "game_state.json"
USER_STATE_PATH = _BASE_DIR / "data" / "user_state.json"
SAVE_DIR = _BASE_DIR / "saves"


class StateManager:
    def __init__(self) -> None:
        self.state: dict[str, Any] = {}
        self.user: dict[str, Any] = {}
        self.load_default_state()
        self.load_user_state()

    def is_running(self) -> bool:
        return bool(self.state.get('running', True))

    def get_phase(self) -> str:
        phase = self.state.get('phase', self.state.get('game_phase', 'EXPLORATION'))
        return phase if isinstance(phase, str) else 'EXPLORATION'

    # -- Room helpers (single source of truth, template-immutable) --

    def get_current_room_id(self) -> str:
        room = self.state.get("player", {}).get("current_room", "lobby")
        if isinstance(room, str) and room in self.state.get("rooms", {}):
            return room
        return "lobby"

    def ensure_spawn(self, room_id: str = "lobby") -> str:
        """Guarantee a valid spawn point (default lobby)."""
        rooms = self.state.get("rooms", {})
        player = self.state.setdefault("player", {})
        current = player.get("current_room")
        if not isinstance(current, str) or current not in rooms:
            player["current_room"] = room_id if room_id in rooms else next(iter(rooms), "lobby")
        return player["current_room"]

    def get_room_data(self, room_id: str) -> dict[str, Any]:
        rooms = self.state.get("rooms", {})
        if isinstance(rooms, dict):
            data = rooms.get(room_id, {})
            if isinstance(data, dict):
                return data
        return {}

    def get_inventory(self) -> list[str]:
        player = self.state.setdefault("player", {})
        if not isinstance(player, dict):
            self.state["player"] = player = {}
        inv = player.setdefault("inventory", [])
        return inv if isinstance(inv, list) else []

    def current_room(self) -> Any:
        """Return the active Room object (specialised subclass when registered)."""
        from .room import room_for

        room_id = self.get_current_room_id()
        return room_for(room_id, self.get_room_data(room_id))

    def move_player(self, destination: str) -> tuple[bool, str]:
        """Move by direction ('north'/'n') or adjacent room id/name.

        Adjacent-only: a room name is accepted only if it appears in the
        current room's exits values. Returns (ok, next_room_id or message).
        """
        from .parser import ROOM_ALIASES, resolve_room_target
        from .room import room_for

        current_id = self.get_current_room_id()
        current_data = self.get_room_data(current_id)
        exits = current_data.get("exits") or {}
        target = resolve_room_target(destination)
        if target in ROOM_ALIASES.values():
            direction = ROOM_ALIASES.get(target, target)
            target_id = exits.get(direction)
        else:
            target_id = target if target in exits.values() else None
        if not target_id:
            adjacent = ", ".join(sorted(set(exits.values()))) or "nowhere"
            return False, f"You cannot go {destination} from here. Adjacent: {adjacent}."
        target_data = self.get_room_data(target_id)
        if not target_data:
            return False, f"Unknown destination '{target_id}'."
        room = room_for(target_id, target_data)
        ok, reason = room.can_enter(self.get_inventory())
        if not ok:
            return False, reason
        self.state["player"]["current_room"] = target_id
        return True, target_id

    def load_default_state(self) -> None:
        """Loads a fresh instance from the master game_state.json data template."""
        with open(GAME_STATE_PATH, encoding="utf-8") as f:
            self.state = json.load(f)

    def load_user_state(self) -> None:
        """Loads a fresh instance from the master user_state.json data template."""
        with open(USER_STATE_PATH, encoding="utf-8") as f:
            self.user = json.load(f)

    def save_to_file(self, filename: str = "save_slot_1.json") -> None:
        """Persists current runtime state to disk."""
        os.makedirs(SAVE_DIR, exist_ok=True)
        save_path = os.path.join(SAVE_DIR, filename)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4)
        print(f"[System] Game saved to {save_path}")

    def load_from_file(self, filename: str = "save_slot_1.json") -> bool:
        """Loads a saved game file into active memory."""
        save_path = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(save_path):
            print("[System] No save file found.")
            return False

        with open(save_path, encoding="utf-8") as f:
            self.state = json.load(f)
        print(f"[System] Loaded saved file from {save_path}")
        return True