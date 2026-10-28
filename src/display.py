import re

from subprocess import run

from .utils.colors import BOLD, BRIGHT_MAGENTA, BRIGHT_YELLOW, DIM, BRIGHT_GREEN, CYAN, \
    BRIGHT_WHITE, RED, WHITE


def colorize(text: str, color_code: str) -> str:
    from .state import state
    return f"{color_code}{text}\033[0m" if state["enable_colors"] else text

def out(text: str = "", end: str | None = None) -> None:
    import builtins

    builtins.print(safe(text), end=end)

def draw_line(char: str = "-") -> None:
    from .state import state

    out(colorize(char * state["terminal_width"], "\033[2m"))

def safe(text: str) -> str:
    table = str.maketrans({"─": "-", "═": "=", "•": "*", "→": "->", "←": "<-"})
    text = text.translate(table)
    try:
        text.encode("cp1252")
        return text
    except UnicodeEncodeError:
        return text.encode("cp1252", errors="replace").decode("cp1252")

def clear() -> None:
    """Clear the terminal screen (Windows/posix/PyCharm-safe)."""
    try:
        from rich.console import Console

        Console().clear()
    except ModuleNotFoundError:
        import os

        if os.getenv("PYCHARM_HOSTED"):
            import builtins

            builtins.print("\n" * 50)
        else:
            run(["cls" if os.name == "nt" else "clear"], shell=True)

def header(content: str | None = None) -> None:
    from .state import state

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    draw_line("═")

    out(
        colorize(f"[{state['game_state']['phase']}]", BRIGHT_MAGENTA)
    )

    if content:
        visible_len = len(re.sub(r"\x1b\[[0-9;]*m", "", content))
        space_needed = max(1, state["terminal_width"] - visible_len - len(state["player"]["name"]))
        out(content, end=f"{' ' * space_needed}")
        out(colorize(f"{state['player']['name'].upper()}", DIM))
    else:
        space_needed = max(
            1,
            state["terminal_width"] - len(f"LOCATION: {room_data['name']}") - len(
                state["player"]["name"]
            ),
        )
        out(
            colorize(f"LOCATION: {room_data['name']}", BRIGHT_YELLOW + BOLD),
            end=f"{' ' * space_needed}"
        )
        out(colorize(f"{state['player']['name'].upper()}", DIM))
    out(colorize(text=f"{state['game_state']['duration']['value']}", color_code=DIM + BOLD), end=" ")
    out(colorize(text=f"{'[PAUSED]' if state['game_state']['duration']['pause'] else ''}", color_code=DIM))

    draw_line("═")

def footer():
    from .state import state
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    # Exits
    exits = room_data.get("exits") or {}
    if exits:
        formatted_exits = []
        for direction, target in exits.items():
            target_name = state["rooms"].get(target, {}).get("name", target)
            formatted_exits.append(f"{direction.upper()} -> {target_name}")
        out(colorize(f"Exits: {', '.join(formatted_exits)}", CYAN))
    else:
        out(colorize("Exits: None available.", RED))

    # Loose Items
    room_items = room_data.get("items") or []
    if room_items:
        out(colorize(text="\nItems in area:", color_code=BRIGHT_WHITE + BOLD))
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
    interactables = room_data.get("interactables") or room_data.get("interactable") or {}
    if interactables:
        out(colorize("\nInteractables:", DIM + BOLD))
        for interactable in interactables.keys():
            out(f"  • {colorize(interactable, WHITE)}")

    out()

