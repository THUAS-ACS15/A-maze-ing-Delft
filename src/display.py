"""Terminal output helpers: colouring, safe printing, screen clearing, and the header/footer chrome.

All game output should go through :func:`out` so text is downgraded to what the Windows ``cp1252`` console can
display. Colouring honours ``state["enable_colors"]``. ``state`` is imported lazily inside functions to avoid a
circular import with :mod:`src.state`, which itself uses this module.
"""

import re

from subprocess import run

from .utils.colors import BOLD, BRIGHT_MAGENTA, BRIGHT_YELLOW, DIM, BRIGHT_GREEN, CYAN, \
    BRIGHT_WHITE, RED, WHITE


def colorize(text: str, color_code: str) -> str:
    """Wrap ``text`` in an ANSI colour code and reset sequence.

    Args:
        text: Text to colour.
        color_code: ANSI escape sequence (see :mod:`src.utils.colors`).

    Returns:
        The coloured text, or ``text`` unchanged when ``state["enable_colors"]`` is falsy.
    """
    from .state import state
    return f"{color_code}{text}\033[0m" if state["enable_colors"] else text

def out(text: str = "", end: str | None = None) -> None:
    """Print ``text`` after making it safe for the console encoding.

    Args:
        text: Text to print.
        end: Line terminator passed to ``print``; ``None`` means the default newline.
    """
    import builtins

    builtins.print(safe(text), end=end)

def draw_line(char: str = "-") -> None:
    """Print a dimmed horizontal rule spanning ``state["terminal_width"]``.

    Args:
        char: Character repeated to build the line.
    """
    from .state import state

    out(colorize(char * state["terminal_width"], "\033[2m"))

def safe(text: str) -> str:
    """Make ``text`` printable on a ``cp1252`` console.

    Box-drawing and arrow characters are first transliterated to ASCII; any remaining unencodable character is
    replaced with ``?`` rather than raising.

    Args:
        text: Text that may contain non-cp1252 characters.

    Returns:
        Text that can always be encoded as ``cp1252``.
    """
    # Transliterate the glyphs the game uses that cp1252 cannot encode.
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
    """Print the top banner: phase, location (or custom ``content``), player name, elapsed time and pause marker.

    Args:
        content: Optional title shown instead of ``LOCATION: <room name>`` (e.g. ``"INVENTORY"``).
            May contain ANSI codes.
    """
    from .state import state

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    draw_line("═")

    out(
        colorize(f"[{state['game_state']['phase']}]", BRIGHT_MAGENTA)
    )

    if content:
        # Strip ANSI colour codes so padding is computed from the visible width only.
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
    """Print the exits, loose items and interactables of the current room.

    The room's ``interactables`` key is read with a fallback to the legacy singular ``interactable`` spelling.
    """
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

