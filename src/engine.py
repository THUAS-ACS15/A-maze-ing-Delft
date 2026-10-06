from .state import StateManager
from .parser import CommandParser
from .client import AIClient
from .display import DisplayManager
from .a_maze_ing_delft import print_logo


class Engine:
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.parser = CommandParser()
        self.ai_client = AIClient()
        self.display = DisplayManager()
        self._last_room_id: str | None = None

    def run(self) -> None:
        self.state.ensure_spawn("lobby")
        while self.state.is_running():
            phase = self.state.get_phase()

            if phase == "EXPLORATION":
                self.handle_exploration_turn()
            elif phase == "ASSEMBLY":
                self.handle_assembly_turn()
            elif phase == "CHAT_MODE":
                self.handle_chat_turn()
            else:
                self.handle_exploration_turn()

    def get_input(self) -> str:
        return input("\n> ")

    def _render_current_room(self) -> None:
        room_id = self.state.get_current_room_id()
        room_data = self.state.get_room_data(room_id)
        items_db = self.state.state.get("items", {})
        self.display.render_room(room_id, room_data, items_db)
        self._last_room_id = room_id

    def handle_exploration_turn(self) -> None:
        """Single prompt cycle; run() owns the while loop (lobby spawn)."""
        room_id = self.state.get_current_room_id()
        if self._last_room_id != room_id:
            self._render_current_room()

        raw = self.get_input()
        verb, details = self.parser.parse(raw)

        if verb == "EMPTY":
            return
        if verb == "UNKNOWN":
            print("I don't understand that command. Type 'help' for actions.")
            return
        if verb == "INVALID":
            print(details.get("message", "Invalid command."))
            return
        if verb == "quit":
            self.state.state["running"] = False
            print("Goodbye.")
            return
        if verb == "help":
            self.display.render_help(self.state.get_phase())
            return
        if verb == "clear":
            self.display.clear()
            self._render_current_room()
            return
        if verb == "look":
            self._render_current_room()
            return
        if verb == "inventory":
            self.display.render_inventory(
                self.state.get_inventory(), self.state.state.get("items", {}))
            return
        if verb == "save":
            self.state.save_to_file(details.get("target", "save_slot_1.json"))
            return
        if verb == "load":
            if self.state.load_from_file(details.get("target", "save_slot_1.json")):
                self.state.ensure_spawn("lobby")
                self._last_room_id = None
            return

        room = self.state.current_room()

        if verb == "go":
            target = details.get("target", "")
            ok, result = self.state.move_player(target)
            if not ok:
                print(result)
                return
            self._render_current_room()
            return
        if verb == "inspect":
            target = details.get("target", "")
            if target == "workbench" and self.state.get_current_room_id() == "lab_d2001":
                self.display.render_workbench(
                    self.state.state.get("workbench", {}),
                    self.state.state.get("items", {}))
                return
            if target == "terminal" and self.state.get_current_room_id() == "lobby":
                raw_text = room.interactables.get("terminal", "A maze ing Delft")
                full_msg = raw_text if isinstance(raw_text, str) else str(raw_text)
                print_logo()
                print(full_msg)
                return
            print(room.on_inspect(target, self.state))
            return
        if verb == "take":
            ok, msg = room.on_take(details.get("target", ""), self.state)
            print(msg)
            return
        if verb == "use":
            item = details.get("target", "")
            indirect = details.get("indirect")
            ok, msg = room.on_use(item, indirect, self.state)
            print(msg)
            if self.state.get_phase() != "EXPLORATION":
                self._last_room_id = None
            return
        if verb == "activate":
            current = self.state.current_room()
            handler = getattr(current, "on_activate", None)
            if handler is None:
                print("Nothing to activate here.")
                return
            ok, msg = handler(self.state)
            print(msg)
            if ok:
                self._last_room_id = None
            return
        print(f"Unhandled command '{verb}'.")

    def handle_assembly_turn(self) -> None:
        return

    def handle_chat_turn(self) -> None:
        return