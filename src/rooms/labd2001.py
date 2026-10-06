
from ..room import Room


class LabD2001(Room):
    """Workbench assembly: `use <part> on workbench`, `activate` when ready."""

    def on_use(self, item_id: str, target: str | None, state) -> tuple[bool, str]:
        if target != "workbench":
            return super().on_use(item_id, target, state)
        wb = state.state.setdefault("workbench", {})
        required = wb.setdefault("required_parts", [])
        installed = wb.setdefault("installed_parts", [])
        inventory = state.state.setdefault("player", {}).setdefault("inventory", [])
        if item_id not in inventory:
            return False, f"You are not carrying '{item_id}'."
        if item_id not in required:
            return False, f"'{item_id}' is not a workbench component."
        if item_id in installed:
            return False, f"'{item_id}' is already installed."
        inventory.remove(item_id)
        installed.append(item_id)
        if len(installed) >= len(required) and required:
            wb["is_ready"] = True
            state.state["game_phase"] = "ASSEMBLY"
            return True, f"{item_id} installed. ALL COMPONENTS INSTALLED — type 'activate'."
        return True, f"{item_id} installed ({len(installed)}/{len(required)})."

    def on_activate(self, state) -> tuple[bool, str]:
        wb = state.state.get("workbench", {})
        if not wb.get("is_ready"):
            missing = len(wb.get("required_parts", [])) - len(wb.get("installed_parts", []))
            return False, f"Assembly incomplete. {missing} part(s) missing."
        state.state["game_phase"] = "CHAT_MODE"
        state.state.setdefault("flags", {})["lab_power_on"] = True
        return True, "A-maze-ing-Delft IS READY FOR INITIALIZATION."
