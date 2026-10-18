from __future__ import annotations

from typing import Any

from .utils.colors import BRIGHT_YELLOW, BOLD, CYAN, RED, BRIGHT_WHITE, BRIGHT_GREEN, DIM, \
    WHITE
from .display_functional import draw_line, out, colorize, clear
from .state_functional import get_state, state

NAME: str | None = None
DESCRIPTION:  str | None = None
EXITS: dict[str, str] | None = None
ROOM_ID: str | None = None
INTERACTABLE: dict[str, str]  = {}
IS_LOCKED: bool | None = None
REQUIRED_ITEM: str | None = None
ITEMS: list[str] | None = None
LAST_ROOM_ID: str | None = None

ROOM_CLASSES: dict[str, str] = {
    "teachers_room_1": "src.rooms.teachers_room_1.teachers_room_1",
    "teachers_room_2": "src.rooms.teachers_room_2.teachers_room_2",
    "lab_d_2001": "src.rooms.lab_d_2001.Lab_d_2001",
}

def init(items: list[Any] | None) -> None:
    global NAME, DESCRIPTION, EXITS, ROOM_ID, INTERACTABLE, IS_LOCKED, REQUIRED_ITEM, ITEMS, IS_LOCKED
    if not NAME and not DESCRIPTION and not EXITS and items is None:
        NAME = ROOM_ID
    ROOM_ID = ROOM_ID
    NAME = NAME or ROOM_ID
    ITEMS = list(items or [])
    INTERACTABLE = dict(INTERACTABLE or {})
    IS_LOCKED = bool(IS_LOCKED) if IS_LOCKED is not None else False
    REQUIRED_ITEM = REQUIRED_ITEM

def get_room() -> dict[str, Any]:
    return get_state("rooms").get(ROOM_ID, {})

def is_restricted(inventory: list | None = None, requires: str | None = None, restricted: bool | None = None) -> tuple[bool, str]:
    current_room = get_state("player").get("current_room")
    if inventory is None:
        inventory = get_state("inventory")

    if restricted is None:
       restricted = get_state("rooms").get(current_room).get("restricted", False)

    if requires is None:
        requires = get_state("rooms").get(current_room).get("requires")

    if requires:
        if requires in (inventory or []):
            return True, ""
        return False, f"The door is locked. Access requires: {REQUIRED_ITEM}."
    if restricted:
        return False, "The door is locked."
    return True, ""

def get_description() -> str | None:
    return DESCRIPTION

def enter() -> str | None:
    get_description()

def look() -> None:
    get_description()

def inspect(target: str) -> tuple[bool, str]:
    current_room = state["player"]["current_room"]
    room = state["rooms"].get(current_room, {})
    interactables = room.get("interactables", room.get("interactable", {}))

    if not isinstance(interactables, dict):
        return False, f"{target.title()} cannot be inspected."

    if target not in interactables:
        return False, f"There is no '{target}' here."

    return True, str(interactables[target])

def take(item_id: str, state) -> tuple[bool, str]:
    rooms = get_state("rooms")
    room_data = rooms.get(ROOM_ID, {})
    room_items = room_data.get("items", [])
    if item_id not in room_items:
        return False, f"There is no '{item_id}' here."
    room_items.remove(item_id)
    state.state.setdefault("player", {}).setdefault("inventory", []).append(item_id)
    return True, f"You picked up {item_id}."

def use(item: str, target: str | None) -> tuple[bool, str]:
    inventory = state["player"]["inventory"]
    if item not in inventory:
        return False, f"You are currently do not have '{item}' in your inventory."
    return False, f"You cannot use that {item} on {target}."

def logout(self, destination: str, state=None) -> str | None:
    """Resolve a direction or adjacent room id/name to a room_id."""
    from .parser import ROOM_ALIASES, resolve_room_target

    target = resolve_room_target(destination)
    if target in ROOM_ALIASES.values():
        return self.exits.get(ROOM_ALIASES.get(target, target))
    if target in self.exits.values():
        return target
    return None


def from_data(cls, room_id: str, data: dict[str, Any]):
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

def room_for(room_id: str, data: dict[str, Any]) -> Any | None:
    """Factory: return specialized subclass if registered, else plain Room."""
    import importlib

    path = ROOM_CLASSES.get(room_id)
    if path:
        module_name, _, class_name = path.rpartition(".")
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls.from_data(room_id, data)
    return None

def render(room_id: str | None = None, room_data: dict[str, Any] | None = None,
                items: dict[str, Any] | None = None, text: str | None = None, asset: str | None = None) -> None:
    """Displays current location, description, exits, items, and interactable features."""
    if room_id is None:
        room_id = state["player"]["current_room"]
    if room_data is None:
        try:
            room_data = state["rooms"][room_id]
        except KeyError:
            current_room = state["player"]["current_room"]
            room_data = state["rooms"][current_room]
    if text is None:
       text = room_data["description"]
    draw_line("═")
    out(
        colorize(f"LOCATION: {room_data["name"]}", BRIGHT_YELLOW + BOLD)
        )
    draw_line("═")

    # Asset
    if asset:
        print(asset)
    # Room Narrative
    out(f"\n{text}\n")

    # Exits
    exits = room_data.get("exits", {})
    if exits:
        formatted_exits = [f"{direction.upper()} -> {target}" for direction, target
                           in exits.items()]
        out(colorize(f"Exits: {', '.join(formatted_exits)}", CYAN))
    else:
        out(colorize("Exits: None available.", RED))

    # Loose Items
    room_items = room_data.get("items", [])
    if room_items:
        out(colorize("\nItems in area:", BRIGHT_WHITE + BOLD))
        for item_id in room_items:
            item_data = state["items"][item_id]
            display_name = item_data.get("name", item_id)
            component_tag = (
                f" {colorize('[ASSEMBLY PART]', BRIGHT_GREEN)}"
                if item_data.get("is_assembly_part")
                else ""
            )
            out(
                f"  • {colorize(display_name, BRIGHT_YELLOW)}{component_tag}"
                )

    # Points of Interest
    interactables = room_data.get("interactables", room_data.get("interactable", {}))
    if interactables:
        out(colorize("\nInteractive Objects:", DIM))
        for poi_key in interactables.keys():
            out(f"  • {colorize(poi_key, WHITE)}")

    out()