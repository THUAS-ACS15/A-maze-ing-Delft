"""Command engine: handlers for every player verb and the main game loop.

:func:`run` loops while ``state["running"]`` is true, calling :func:`src.state.auto` (clock + autosave) and then the
prompt cycle of the current phase (see :mod:`src.phase`). Each cycle parses input with :func:`src.parser.parse` and
hands the result to :func:`commands`, which dispatches to the handlers below.

Handler contract: handlers take the ``details`` dict produced by the parser, mutate :data:`src.state.state`, and
report to the player by rendering text. They return ``None`` and do not raise for ordinary bad input (wrong room,
missing item, locked door). Screens that show information without a room view (inventory, help, status, scoreboard)
pause the game clock; the next :func:`src.room.render` resumes it.

Attributes:
    STATUS_FLAG_LABELS: Player-facing names for the progress flags listed on the status screen.
"""

from datetime import timezone, datetime
import json
import copy
import textwrap

from typing import Any

from .display import header
from .model import get_user, create_user, get_scoreboard_entries
from .rooms.lab_d2_001 import use_on_workbench, workbench
from .rooms.teachers_room_1 import use_desk_code
from .rooms.teachers_room_4 import inspect_computer
from .state import (
    auto,
    help_commands,
    list_saves,
    load,
    normalize_state,
    DEFAULT_GAME_STATE_PATH,
)
from .room import render
from .utils.colors import BRIGHT_CYAN, BOLD, BRIGHT_GREEN, BRIGHT_YELLOW, DIM, \
    BRIGHT_WHITE, RED, INFO, ERROR, SUCCESS
from .display import out, colorize
from .state import spawn,  \
    save, move, state
from .utils.format_timestamp import format_timestamp


STATUS_FLAG_LABELS = {
    "fr1_user_registered": "Front desk registration",
    "tr1_desk_unlocked": "Teachers Room 1 desk unlocked",
    "tr2_whiteboard_inspected": "Teachers Room 2 whiteboard inspected",
    "tr4_drawer_decrypted": "Teachers Room 4 drawer decrypted",
    "tr4_secret_key_copied": "Teachers Room 4 secret key copied",
    "lab_power_on": "Lab power restored",
}


def prompt(message: str | None = None) -> str:
    """Read one line of player input.

    Args:
        message: Optional label shown before the ``>`` marker. Defaults to a bare ``>`` prompt.

    Returns:
        The input with surrounding whitespace stripped.

    Raises:
        EOFError: If standard input is closed.
    """
    if message is None:
        return input("\n> ").strip()
    return input(f"\n{message} >").strip()

def inventory() -> None:
    """Show carried items and how many assembly parts are held. Pauses the game clock."""
    width = int(state["terminal_width"])
    state["game_state"]["duration"]["pause"] = True
    header(colorize(text="INVENTORY", color_code=BRIGHT_CYAN + BOLD))
    if not state["player"]["inventory"]:
        out()
        out(colorize(text="Your inventory is currently empty.".center(width), color_code=DIM))
        out()
        return

    assembly_parts_count = 0
    for item in state["player"]["inventory"]:
        item_data = state["items"][item]

        if item_data["is_assembly_part"]:
            assembly_parts_count += 1
            tag = f" {colorize('[ASSEMBLY PART]', BRIGHT_GREEN)}"
        else:
            tag = ""

        out(f" • {colorize(item_data['name'], BRIGHT_YELLOW)}{tag}")
        out(f"   {colorize(item_data['description'], DIM)}")

    out(
        colorize(
            f"\nAssembly Components in Inventory: {assembly_parts_count}/{len(state['workbench']['required_parts'])}",
            BRIGHT_WHITE
        )
    )
    out()

def helper() -> None:
    """Show the help menu. Pauses the game clock.

    Uses ``rich`` tables when available and plain text otherwise. The ``Assembly`` command group is hidden until the
    ``ASSEMBLY`` phase.
    """
    state["game_state"]["duration"]["pause"] = True
    groups = [
        group for group in help_commands
        if group["title"] != "Assembly" or state["game_state"]["phase"] == "ASSEMBLY"
    ]

    try:
        import os

        from rich.console import Console
        from rich.table import Table

        header(colorize(text="HELP MENU", color_code=INFO + BOLD))
        console = Console(highlight=False, force_terminal=None if os.getenv("NO_COLOR") else True)
        for group in groups:
            table = Table(title=group["title"], show_header=True, header_style="bold")
            table.add_column("Command", style="cyan", no_wrap=True)
            table.add_column("Description")
            table.add_column("Example", style="dim")
            for cmd in group["commands"]:
                table.add_row(cmd["command"], cmd["description"], cmd["example"])
            console.print(table)
    except ModuleNotFoundError:
        out("Available Commands:")
        for group in groups:
            out(f"[{group['title']}]")
            for cmd in group["commands"]:
                out(f"  {cmd['command']:<24} {cmd['description']}  e.g. {cmd['example']}")
        return None

def inspect(details) -> None:
    """Inspect an interactable in the current room.

    Only a few targets are valid, each in one specific room (lobby ``terminal``, ``teachers_room_1`` ``desk``,
    ``lab_d2_001`` ``workbench``, ``teachers_room_2`` ``whiteboard``, ``front_desk`` ``receptionist``,
    ``teachers_room_4`` ``computer``). Anything else renders a "not in this room" error. Inspecting the whiteboard
    sets the ``tr2_whiteboard_inspected`` flag.

    Args:
        details: Parsed details with ``"target"``.
    """
    target = details["target"]
    current_room = state["player"]["current_room"]
    if target == "terminal" and state["player"]["current_room"] == "lobby":
        from .assets.logo import logo
        render(text=state["rooms"]["lobby"]["interactables"]["terminal"], asset=logo)
        return None
    elif target == "desk" and state["player"]["current_room"] == "teachers_room_1":

        if not state["flags"]["tr1_desk_unlocked"]:

            render(
                text=state["rooms"]["teachers_room_1"]["interactables"]["desk"]["hint"]
                )
            return None
        render(
            text=colorize("The desk drawer is open. You already took the keycard.", BRIGHT_GREEN)
        )
        return None
    elif target == "workbench" and state["player"]["current_room"] == "lab_d2_001":
        workbench()
        return None
    elif target == "whiteboard" and state["player"]["current_room"] == "teachers_room_2":
        state["flags"]["tr2_whiteboard_inspected"] = True
        whiteboard = state["rooms"]["teachers_room_2"]["interactables"]["whiteboard"]
        render(text=whiteboard)
        return None
    elif target == "receptionist" and state["player"]["current_room"] == "front_desk":
        receptionist = state["rooms"]["front_desk"]["interactables"]["receptionist"]
        render(text=receptionist)
        return None
    elif target == "computer" and current_room == "teachers_room_4":
        inspect_computer()
        return None
    else:
        render(text=colorize("The item you're trying to inspect is unavailable", color_code=RED))
        return None

def use(details: Any) -> None:
    """Use an item, with behaviour depending on the room.

    In ``teachers_room_1`` the item is treated as a desk code, in ``lab_d2_001`` it is installed on the workbench, and
    elsewhere nothing can be used (the player is told whether the item is missing or simply useless there).

    Args:
        details: Parsed details with ``"target"`` (item) and ``"indirect"`` (optional target).
    """
    item = details["target"]
    target = details["indirect"]
    if state["player"]["current_room"] == "teachers_room_1":
        use_desk_code(item, target)
        return None
    if state["player"]["current_room"] == "lab_d2_001":
        use_on_workbench(item)
        return None
    else:
        pi = state["player"]["inventory"]
        if item not in pi:
            render(
                text=colorize(
                    f"You are currently do not have '{item}' in your inventory.",
                    color_code=RED
                    )
                )
            return None
        render(
            text=colorize(
                f"You cannot use that {item} on {target}.", color_code=RED
            )
        )
        return None

def take(details: Any) -> None:
    """Move an item from the current room into the inventory.

    Args:
        details: Parsed details with ``"target"`` (item id). Renders an error if the item is not in the room.
    """
    item = details["target"]
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    if item not in room_data["items"]:
        render(text=colorize(f"There is no '{item}' here.", color_code=RED))
        return None
    room_data["items"].remove(item)
    state["player"]["inventory"].append(item)
    itm = state["items"][item]
    render(colorize(f"You picked up {itm['name']}", BRIGHT_GREEN))
    return None

def drop(details: Any) -> None:
    """Move an item from the inventory into the current room.

    Args:
        details: Parsed details with ``"target"`` (item id). Renders an error if the item is not carried.

    Raises:
        KeyError: If the target is not a known item id.
    """
    item = details["target"]
    item_data = state["items"][item]
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    if item not in state["player"]["inventory"]:
        render(text=colorize(f"You currently do not have '{item_data['name']}' here.", color_code=RED))
        return None
    state["player"]["inventory"].remove(item)
    state["rooms"][current_room]["items"].append(item)
    render(colorize(f"You dropped {item_data['name']} in {room_data['name']}", BRIGHT_GREEN))
    return None

def exit_game() -> None:
    """Stop the main loop, print the final status screen and a farewell message."""
    state["running"] = False
    status()
    out(colorize(text="Goodbye. see you again soon".center(state["terminal_width"]), color_code=BRIGHT_GREEN))
    return None

def register(details: Any) -> None:
    """Create a user profile and attach it to the player. Only works in ``front_desk``.

    Args:
        details: Parsed details with ``"target"`` (desired name). A taken name or database error is rendered,
            not raised.
    """
    name = details["target"]
    if not state["player"]["current_room"] == "front_desk":
        render(colorize(text="You can only register at the front desk", color_code=RED))
        return None
    user = get_user(name)
    if not user:
       try:
           user_id = create_user(name)
           state["player"]["name"] = name
           state["player"]["id"] = user_id
           render(text=colorize(f"You have successfully registered a profile as {name}", color_code=BRIGHT_GREEN))
           return None
       except Exception as e:
           render(text=colorize(str(e), color_code=RED))
           return None
    render(text=colorize(f"The name '{name}' is already taken. Please try another one.", color_code=RED))
    return None

def login(details: Any) -> None:
    """Attach an existing user profile to the player. Only works in ``front_desk``.

    Args:
        details: Parsed details with ``"target"`` (user name).
    """
    name = details["target"]
    if not state["player"]["current_room"] == "front_desk":
        render(colorize(text="You can only register at the front desk", color_code=RED))
        return None
    if name is None:
        render(text=colorize("Please enter a name", color_code=RED))
        return None
    user = get_user(name)
    if not user:
        render(colorize(f"User '{name}' does not exist", color_code=ERROR))
        return None
    state["player"]["name"] = name
    state["player"]["id"] = user["id"]
    render(colorize(f"You are currently logged in as {name}", color_code=SUCCESS))
    return None

def logout() -> None:
    """Detach the user profile from the player (back to ``guest``). Only works in ``front_desk`` while logged in.

    Game progress is kept; only the identity changes.
    """
    if state["player"]["current_room"] != "front_desk":
        render(colorize(text="You can only complete this operation at the front desk", color_code=ERROR))
        return None
    if not state["player"]["id"]:
        render(colorize(text="You are currently not logged in!", color_code=ERROR))
        return None
    snapshot = copy.deepcopy(state)
    state["player"]["id"] = None
    state["player"]["name"] = "guest"
    render(colorize(text=f"You have been logged out from {snapshot['player']['name']}", color_code=SUCCESS))
    return None


def restart() -> None:
    """Reset the game to the default template, keeping the player's name and id.

    The clock is restarted at ``00:00:00`` and unpaused.
    """
    # Keep a copy only to carry the player's identity across the reset below.
    snapshot = copy.deepcopy(state)
    # Reset in place (clear + update): other modules share a reference to the state dict.
    with open(DEFAULT_GAME_STATE_PATH) as df:
        state.clear()
        state.update(json.load(df))
        normalize_state(state)
        state["player"]["name"] = snapshot["player"]["name"]
        state["player"]["id"] = snapshot["player"]["id"]
        now = datetime.now(timezone.utc).isoformat()
        state["game_state"]["timestamp"] = now
        state["game_state"]["duration"]["last_write"] = now
        state["game_state"]["duration"]["value"] = "00:00:00"
        state["game_state"]["duration"]["pause"] = False
    render(text=colorize("New game!", color_code=BRIGHT_GREEN))

def scoreboard() -> None:
    """Show the ranked scoreboard (best score first, then fastest total time)."""
    width = int(state["terminal_width"])
    entries = get_scoreboard_entries()
    header(colorize(text="GAME SCOREBOARD", color_code=INFO + BOLD))
    if not entries:
        out()
        out(colorize(text="No entries found!".center(width), color_code=DIM))
        return None

    rows = []
    for rank, entry in enumerate(entries, start=1):
        user = get_user(entry["user_id"])
        player_name = user["name"] if user else f"Unknown ({entry['user_id']})"
        rows.append((rank, player_name, entry))

    out(
        f"{'Rank':<6}{'Player':<20}{'Score':>8}  "
        f"{'Avg Room':<10}{'Exploration':<12}{'Assembly':<10}"
    )
    for rank, player_name, entry in rows:
        out(
            f"{rank:<6}{player_name:<20}{entry['score']:>8}  "
            f"{entry['avg_room_time']:<10}{entry['exploration_time']:<12}"
            f"{entry['assembly_time']:<10}"
        )

    return None

def _wrap_status_text(text: str, width: int) -> list[str]:
    """Wrap status text, preferring comma-separated item boundaries.

    Args:
        text: Text to wrap.
        width: Maximum line width.

    Returns:
        At least one line; items are kept whole where they fit, otherwise long words are broken.
    """
    if ", " in text:
        lines = []
        current = ""
        for item in text.split(", "):
            candidate = f"{current}, {item}" if current else item
            if len(candidate) <= width:
                current = candidate
            else:
                if current:
                    lines.append(f"{current},")
                current = item
        if current:
            lines.append(current)

        wrapped = []
        for line in lines:
            if len(line) <= width:
                wrapped.append(line)
            else:
                wrapped.extend(
                    textwrap.wrap(line, width=width, break_long_words=True) or [""]
                )
        return wrapped or [""]

    return textwrap.wrap(text, width=width, break_long_words=True) or [""]


def _print_status_row(label: str, value: str, width: int) -> None:
    """Print one status row, wrapping long values at ``width``.

    Short values are right-aligned; wrapped values continue on indented lines. Multi-line values are wrapped per line.

    Args:
        label: Row label.
        value: Row value, possibly containing newlines.
        width: Total terminal width.
    """
    prefix = f" {label}:"
    indent = " " * (len(prefix) + 1)
    available = max(1, width - len(prefix) - 2)
    first, *rest = value.splitlines() or [""]

    chunks = _wrap_status_text(first, available)
    if len(chunks) == 1:
        gap = max(1, width - len(prefix) - len(chunks[0]) - 1)
        out(f"{prefix}{' ' * gap}{chunks[0]}")
    else:
        out(f"{prefix} {chunks[0]}")
        for chunk in chunks[1:]:
            out(f"{indent}{chunk}")

    for line in rest:
        for chunk in _wrap_status_text(line, available):
            out(f"{indent}{chunk}")



def status() -> None:
    """Show the status screen: player, room, phase, time, exploration progress, challenges and inventory.

    Pauses the game clock.
    """
    state["game_state"]["duration"]["pause"] = True
    header(colorize(text="STATUS MENU", color_code=BRIGHT_YELLOW + BOLD))

    player = state["player"]
    game_state = state["game_state"]
    rooms = state["rooms"]
    items = state["items"]
    flags = state["flags"]
    wb = state["workbench"]

    current_room = player["current_room"]
    room_name = rooms[current_room]["name"]
    timestamp = game_state["timestamp"]
    start_time = format_timestamp(timestamp) if timestamp else "Unknown"
    duration = game_state["duration"]["value"] or "00:00:00"

    # Order-preserving de-duplication of visited rooms (history plus current room).
    visited_ids = list(dict.fromkeys([*player.get("move", []), current_room]))
    visited_names = [
        rooms[room_id]["name"] for room_id in visited_ids
    ]
    recent_visited = visited_names[-5:]
    visited_text = ", ".join(recent_visited) or "None"
    if len(visited_names) > 5:
        visited_text = f"... {visited_text}"
    total_rooms = len(rooms)
    explored_percent = round(len(visited_ids) / total_rooms * 100)

    completed = [
        STATUS_FLAG_LABELS.get(flag, flag.replace("_", " ").title())
        for flag, enabled in flags.items()
        if enabled
    ]
    installed = len(wb["installed_parts"])

    inv = player["inventory"]
    inventory_names = [
        items.get(item_id, {}).get("name", item_id) for item_id in inv
    ]
    assembly_parts = sum(
        1 for item_id in inv if items.get(item_id, {}).get("is_assembly_part")
    )

    required = len(wb["required_parts"])
    ready_text = "ready" if wb["is_ready"] else "not ready"

    inventory_items = ", ".join(inventory_names) or "Empty"

    challenge_text = f"{len(completed)}/{len(flags)}"
    if completed:
        challenge_text += " " + ", ".join(completed)

    rows = [
        ("Name", player["name"].title()),
        ("Room", room_name),
        ("Phase", game_state["phase"]),
        None,
        ("Started", start_time),
        ("Time spent", duration),
        None,
        ("Explored", f"{len(visited_ids)}/{total_rooms} ({explored_percent}%)"),
        ("Visited", visited_text),
        ("Challenges", challenge_text),
        ("Assembly", f"{installed}/{required} installed ({ready_text})"),
        None,
        ("Inventory", inventory_items),
        ("Assembly parts", str(assembly_parts)),
    ]


    for row in rows:
        if row is None:
            out()
            continue
        label, value = row
        _print_status_row(label, value, state["terminal_width"])

    out()
    return None


def commands(verb, details) -> None:
    """Dispatch a parsed command to its handler.

    ``clear`` and ``activate`` are handled elsewhere (screen clearing and :mod:`src.phase`), and verbs without a
    handler (including ``UNKNOWN``, ``INVALID`` and ``EMPTY``) are silently ignored here; callers report those.

    Args:
        verb: Canonical verb returned by :func:`src.parser.parse`.
        details: Details dict returned by :func:`src.parser.parse`.
    """
    if verb == "quit":
        exit_game()
        return
    if verb == "restart":
        restart()
        return
    elif verb == "help":
        helper()
        return
    elif verb == "scoreboard":
        scoreboard()
        return
    elif verb == "status":
        status()
        return
    elif verb == "inventory":
        inventory()
        return
    elif verb == "use":
        use(details)
        return
    elif verb == "register":
        register(details)
        return
    elif verb == "login":
        login(details)
        return
    elif verb == "logout":
        logout()
        return
    elif verb == "save":
        save(details)
        return
    elif verb == "saves":
        list_saves()
        return
    elif verb == "load":
        load(details)
        return
    elif verb == "inspect":
        inspect(details)
        return
    elif verb == "look":
        render()
        return
    elif verb == "take":
        take(details)
        return
    elif verb == "drop":
        drop(details)
        return
    elif verb == "go":
        move(details)
        return


def run() -> None:
    # Imported lazily to break the engine_functional <-> phase circular import.
    """Run the main game loop until ``state["running"]`` becomes false."""
    from .phase import exploration, assembly, chat
    spawn()
    while state["running"]:
        auto()
        if state["game_state"]["phase"] == "EXPLORATION":
            exploration()
        elif state["game_state"]["phase"] == "ASSEMBLY":
            assembly()
        elif state["game_state"]["phase"] == "CHAT":
            chat()
        else:
            exploration()