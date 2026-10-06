"""Room model (src/Room.py).

Data-driven base class + puzzle subclasses.
Rooms are defined in game_state.json under ``rooms`` (see STATE_SCHEMA.md).
Engine owns the input loop; Room only decides what happens for
look / inspect / take / use / enter / exit.
"""

from __future__ import annotations

from typing import Any

# Subclasses live in src/rooms/ and are imported lazily in room_for()
# to avoid a circular import (src/rooms/*.py imports Room from here).

ROOM_CLASSES: dict[str, str] = {
    "teachers_room_1": "src.rooms.teachersroom1.TeachersRoom1",
    "teachers_room_2": "src.rooms.teachersroom2.TeachersRoom2",
    "lab_d2001": "src.rooms.labd2001.LabD2001",
}



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
        interactables = data.get("interactables", data.get("interactable", {}))
        return cls(
            room_id=room_id,
            name=data.get("name", room_id),
            description=data.get("description", ""),
            exits=dict(data.get("exits", {})),
            items=list(data.get("items", [])),
            interactables=dict(interactables or {}),
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

    def on_exit(self, destination: str, state=None) -> str | None:
        """Resolve a direction or adjacent room id/name to a room_id."""
        from .parser import ROOM_ALIASES, resolve_room_target

        target = resolve_room_target(destination)
        if target in ROOM_ALIASES.values():
            return self.exits.get(ROOM_ALIASES.get(target, target))
        if target in self.exits.values():
            return target
        return None


def room_for(room_id: str, data: dict[str, Any]) -> Room:
    """Factory: return specialised subclass if registered, else plain Room."""
    import importlib

    path = ROOM_CLASSES.get(room_id)
    if path:
        module_name, _, class_name = path.rpartition(".")
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls.from_data(room_id, data)
    return Room.from_data(room_id, data)
