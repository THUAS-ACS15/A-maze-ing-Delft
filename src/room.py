from __future__ import annotations

from .display import header
from .utils.colors import BRIGHT_YELLOW, BOLD, CYAN, RED, BRIGHT_WHITE, BRIGHT_GREEN, \
    DIM, \
    WHITE
from .display import out, colorize
from .state import state

def render(text: str | None = None, asset: str | None = None) -> None:
    """Displays current location, description, exits, items, and interactable features."""

    current_room = state["player"]["current_room"]

    room_data = state["rooms"][current_room]

    if text is None:
       text = room_data["description"]
    header()

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