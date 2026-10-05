import json
import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
GAME_STATE_PATH = _BASE_DIR / "data" / "game_state.json"
USER_STATE_PATH = _BASE_DIR / "data" / "user_state.json"
SAVE_DIR = _BASE_DIR / "saves"


class StateManager:
    def __init__(self):
        self.state: dict =  {}
        self.user: dict = {}
        self.load_default_state()
        self.load_user_state()

    def is_running(self):
        return self.state.get('running', True)

    def get_phase(self):
        return self.state.get('phase', self.state.get('game_phase', 'EXPLORATION'))

    # -- Room helpers (single source of truth, template-immutable) --

    def get_current_room_id(self) -> str:
        room = self.state.get("player", {}).get("current_room", "lobby")
        return room if isinstance(room, str) else "lobby"

    def get_room_data(self, room_id: str) -> dict:
        return self.state.get("rooms", {}).get(room_id, {})

    def get_inventory(self) -> list:
        return self.state.setdefault("player", {}).setdefault("inventory", [])

    def current_room(self):
        """Return the active Room object (specialised subclass when registered)."""
        from .Room import room_for

        room_id = self.get_current_room_id()
        return room_for(room_id, self.get_room_data(room_id))

    def move_player(self, direction: str):
        """Move via exits dict. Returns (ok, message/next_room_id)."""
        from .Room import room_for

        current_id = self.get_current_room_id()
        current_data = self.get_room_data(current_id)
        target_id = (current_data.get("exits") or {}).get(direction)
        if not target_id:
            return False, f"You cannot go {direction} from here."
        target_data = self.get_room_data(target_id)
        if not target_data:
            return False, f"Unknown destination '{target_id}'."
        room = room_for(target_id, target_data)
        ok, reason = room.can_enter(self.get_inventory())
        if not ok:
            return False, reason
        self.state["player"]["current_room"] = target_id
        return True, target_id

    def load_default_state(self):
        """Loads a fresh instance from the master game_state.json data template."""
        with open(GAME_STATE_PATH, encoding="utf-8") as f:
            self.state = json.load(f)

    def load_user_state(self):
        """Loads a fresh instance from the master user_state.json data template."""
        with open(USER_STATE_PATH, encoding="utf-8") as f:
            self.user = json.load(f)

    def save_to_file(self, filename="save_slot_1.json"):
        """Persists current runtime state to disk."""
        os.makedirs(SAVE_DIR, exist_ok=True)
        save_path = os.path.join(SAVE_DIR, filename)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4)
        print(f"[System] Game saved to {save_path}")

    def load_from_file(self, filename="save_slot_1.json"):
        """Loads a saved game file into active memory."""
        save_path = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(save_path):
            print("[System] No save file found.")
            return False

        with open(save_path, encoding="utf-8") as f:
            self.state = json.load(f)
        print(f"[System] Loaded saved file from {save_path}")
        return True