import json
import os

DATA_PATH = os.path.join("data", "game_state.json")
SAVE_DIR = "saves"


class GameStateManager:
    def __init__(self):
        self.state = {}
        self.load_default_state()

    def load_default_state(self):
        """Loads a fresh instance from the master game_state.json data template."""
        with open(DATA_PATH, encoding="utf-8") as f:
            self.state = json.load(f)

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
        print(f"[System] Loaded save file from {save_path}")
        return True