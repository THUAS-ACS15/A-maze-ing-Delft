"""Room model (src/room.py).

Data-driven base class + puzzle subclasses.
Rooms are defined in game_state.json under ``rooms`` (see STATE_SCHEMA.md).
Engine owns the input loop; Room only decides what happens for
look / inspect / take / use / enter / exit.
"""

from __future__ import annotations

from typing import Any


class Room:
    """Parent class. Extend only when a room has custom puzzle logic."""

    room_id: str
    name: str
    description: str

    def __init__(
        self,
        room_id: str,
        name: str = "",
        description: str = "",
        exits: dict[str, str] | None = None,
        items: list | None = None,
        interactables: dict[str, Any] | None = None,
        is_locked: bool = False,
        required_item: str | None = None,
    ) -> None:
        # Backwards compat: old stub was Room(name).
        # Room("lobby") -> room_id="lobby", name="lobby".
        if not name and not description and not exits and items is None:
            name = room_id
        self.room_id = room_id
        self.name = name or room_id
        self.description = description
        self.exits = exits or {}
        self.items = list(items or [])
        self.interactables = dict(interactables or {})
        self.is_locked = bool(is_locked) if is_locked is not None else False
        self.required_item = required_item

    @classmethod
    def from_data(cls, room_id: str, data: dict[str, Any]) -> Room:
        return cls(
            room_id=room_id,
            name=data.get("name", room_id),
            description=data.get("description", ""),
            exits=dict(data.get("exits", {})),
            items=list(data.get("items", [])),
            interactables=dict(data.get("interactables", {})),
            is_locked=data.get("is_locked", False),
            required_item=data.get("required_item"),
        )

    # -- generic behaviour (override only on_* hooks below) --

    def can_enter(self, inventory: list) -> tuple[bool, str]:
        if self.required_item and self.required_item not in (inventory or []):
            return False, f"The door is locked. Access requires: {self.required_item}."
        if self.is_locked:
            return False, "The door is locked."
        return True, ""

    def on_enter(self, state) -> str:
        return self.description

    def on_look(self, state=None) -> str:
        return self.description

    def on_inspect(self, target: str, state) -> str:
        data = self.interactables.get(target)
        if data is None:
            return f"There is no '{target}' here."
        if isinstance(data, dict):
            return str(data.get("hint", data.get("description", f"You inspect the {target}.")))
        return str(data)

    def on_take(self, item_id: str, state) -> tuple[bool, str]:
        rooms = state.state.get("rooms", {})
        room_data = rooms.get(self.room_id, {})
        room_items = room_data.get("items", [])
        if item_id not in room_items:
            return False, f"There is no '{item_id}' here."
        room_items.remove(item_id)
        state.state.setdefault("player", {}).setdefault("inventory", []).append(item_id)
        return True, f"You picked up {item_id}."

    def on_use(self, item_id: str, target: str | None, state) -> tuple[bool, str]:
        inventory = state.state.get("player", {}).get("inventory", [])
        if item_id not in inventory:
            return False, f"You are not carrying '{item_id}'."
        return False, "Nothing happens."

    def on_exit(self, direction: str, state) -> str | None:
        return self.exits.get(direction)


class TeachersRoom1(Room):
    """Desk keypad puzzle: code '2015' -> Level-1 Staff Keycard."""

    DESK_CODE = "2015"
    REWARD = "keycard_lvl1"

    def on_inspect(self, target: str, state) -> str:
        if target != "desk":
            return super().on_inspect(target, state)
        flags = state.state.setdefault("flags", {})
        if flags.get("tr1_desk_unlocked"):
            return "The desk drawer is open. You already took the keycard."
        desk = self.interactables.get("desk", {})
        hint = desk.get("hint", "Keypad hint: 'Room number where CS101 was held.'") if isinstance(desk, dict) else desk
        return f"A locked desk with a keypad. {hint} (use: 'use 2015 on desk')"

    def on_use(self, item_id: str, target: str | None, state) -> tuple[bool, str]:
        # Accept both `use 2015 on desk` and `enter 2015` style via item_id==code.
        code = item_id if (target == "desk" or target is None) else None
        if target == "desk" or (target is None and item_id == self.DESK_CODE):
            flags = state.state.setdefault("flags", {})
            if flags.get("tr1_desk_unlocked"):
                return False, "The desk is already unlocked."
            if code == self.DESK_CODE:
                flags["tr1_desk_unlocked"] = True
                inv = state.state.setdefault("player", {}).setdefault("inventory", [])
                if self.REWARD not in inv:
                    inv.append(self.REWARD)
                return True, "Keypad clicks green. You obtain the Level-1 Staff Keycard."
            return False, "Keypad buzzes red: Incorrect code entered."
        return super().on_use(item_id, target, state)


class TeachersRoom2(Room):
    """Whiteboard puzzle: inspecting reveals Wi-Fi pass, sets flag."""

    def on_inspect(self, target: str, state) -> str:
        text = super().on_inspect(target, state)
        if target == "whiteboard":
            state.state.setdefault("flags", {})["tr2_whiteboard_inspected"] = True
        return text


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


ROOM_CLASSES = {
    "teachers_room_1": TeachersRoom1,
    "teachers_room_2": TeachersRoom2,
    "lab_d2001": LabD2001,
}


def room_for(room_id: str, data: dict[str, Any]) -> Room:
    """Factory: return specialised subclass if registered, else plain Room."""
    cls = ROOM_CLASSES.get(room_id, Room)
    return cls.from_data(room_id, data)
