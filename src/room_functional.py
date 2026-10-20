from __future__ import annotations

from typing import Any

from .utils.chat import respond
from .utils.colors import BRIGHT_YELLOW, BOLD, CYAN, RED, BRIGHT_WHITE, BRIGHT_GREEN, DIM, \
    WHITE
from .display_functional import draw_line, out, colorize, clear
from .state_functional import state


def inspect(target: str) -> tuple[bool, str]:
    current_room = state["player"]["current_room"]
    room = state["rooms"][current_room]
    interactables = room["interactables"]

    if not isinstance(interactables, dict):
        return False, f"{target.title()} cannot be inspected."

    if target not in interactables:
        return False, f"There is either no '{target}' here or '{target}' is not in the interactables."

    return True, str(interactables[target])

def take(item: str) -> tuple[bool, str]:
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    if item not in room_data["items"]:
        return False, f"There is no '{item}' here."
    room_data["items"].remove(item)
    state["player"]["inventory"].append(item)
    item = state["items"][item]
    return True, f"You picked up {item["name"]}"

def use(item: str, target: str | None) -> tuple[bool, str]:
    inventory = state["player"]["inventory"]
    if item not in inventory:
        return False, f"You are currently do not have '{item}' in your inventory."
    return False, f"You cannot use that {item} on {target}."


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



def render_chat(text: str | None = None) -> None:
    """Displays workbench assembly status in Lab D 2001."""

    installed_parts = state["workbench"]["installed_parts"]
    required_parts = state["workbench"]["required_parts"]

    draw_line("═")
    out(
        colorize(
            "CHAT", BRIGHT_GREEN + BOLD
        )
    )
    draw_line("═")
    # out(f"Progress: {len(installed_parts)} / {len(required_parts)} components installed.\n")

    # for part in required_parts:
    #     item_data = state["items"][part]
    #
    #     if part in installed_parts:
    #         status = colorize(
    #             "[ INSTALLED ]", BRIGHT_GREEN + BOLD
    #         )
    #     else:
    #         status = colorize("[ MISSING   ]", RED + DIM)
    #
    #     out(f" {status} - {item_data['name']}")
    if text is None:
        return
    out()
    respond(text)
    out()
    # if len(installed_parts) == len(required_parts):
    #     command = text if text else "Type 'activate' or 'power on' to start the neural link."
    #     out(
    #         colorize(
    #             ">> ALL CORE COMPONENTS INSTALLED <<",
    #             BRIGHT_GREEN + BOLD
    #         )
    #     )
    #     out(
    #         colorize(
    #             command,
    #             BRIGHT_YELLOW
    #         )
    #     )
    # else:
    #     remaining = len(required_parts) - len(installed_parts)
    #     if text:
    #       print(text)
    #     out(
    #         colorize(
    #             f"Locate remaining {remaining} part(s) to complete assembly.",
    #             DIM
    #         )
    #     )
    return