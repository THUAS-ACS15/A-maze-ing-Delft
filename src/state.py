"""Game state: loading, autosave, manual saves and room movement.

The whole game lives in one mutable module-level dict, :data:`state`, shared by reference with every other module,
so it is only ever mutated in place (``clear()``/``update()``), never rebound after import.

Persistence contract:

* ``data/default_state.json`` is the pristine template; ``data/user_state.json`` is the live autosave, created from
  the template by :func:`init` when missing or empty.
* :func:`auto` rewrites ``user_state.json`` on every main-loop tick, except while the timer is paused.
* :func:`save` writes a named snapshot ``data/saves/<slot>.json`` plus a row in the ``saves`` table. It requires a
  registered player and never overwrites an existing slot.
* :func:`load` replaces :data:`state` from a slot file owned by the logged-in user.
* Older saves are upgraded on load by :func:`normalize_state` (legacy room ids, missing terminal data, duration
  schema).

Timer contract: ``state["game_state"]["duration"]`` holds ``value`` (``H:MM:SS`` text), ``last_write`` (ISO UTC
timestamp of the last tick) and ``pause``. Elapsed time is added on each :func:`auto` tick unless paused.

Attributes:
    state: The live game state.
    help_commands: Help menu groups loaded from ``data/help_state.json``.
    DEFAULT_GAME_STATE_PATH: Path of the pristine state template.
    USER_STATE_PATH: Path of the live autosave.
    HELP_COMMANDS_PATH: Path of the help menu data.
    SAVE_DIR: Directory holding named save slots.
"""

from __future__ import annotations

import json
import os
import re

from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from .utils.parse_time import parse_time_str
from .utils.generate_save_slot import next_save_slot
from .utils.format_timestamp import format_timestamp
from .model import create_save, get_user_saves, get_user_save
from .display import colorize, header, out
from .utils.colors import RED, BRIGHT_GREEN, BRIGHT_RED, DIM, CYAN

from .utils.duration import calculate_duration

_BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_GAME_STATE_PATH = DATA_DIR / "default_state.json"
USER_STATE_PATH = DATA_DIR / "user_state.json"
HELP_COMMANDS_PATH = DATA_DIR / "help_state.json"
SAVE_DIR = DATA_DIR / "saves"

# Ensure target folder exists
USER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
state: dict = {}
help_commands: list = []

_LEGACY_ROOM_IDS = {"teacher_room_4": "teachers_room_4"}


def _migrate_room_ids(state_data: dict) -> None:
    """Rename legacy room ids in place (rooms, exits, current room, history, previous room).

    Args:
        state_data: State dict to upgrade. Malformed sections are skipped rather than raising.
    """
    rooms = state_data.get("rooms")
    player = state_data.get("player")
    for old, new in _LEGACY_ROOM_IDS.items():
        if isinstance(rooms, dict):
            if old in rooms:
                legacy_room = rooms.pop(old)
                rooms.setdefault(new, legacy_room)
            for room in rooms.values():
                exits = room.get("exits") if isinstance(room, dict) else None
                if isinstance(exits, dict):
                    for direction, target in exits.items():
                        if target == old:
                            exits[direction] = new
        if isinstance(player, dict):
            if player.get("current_room") == old:
                player["current_room"] = new
            for key in ("move", "forward"):
                history = player.get(key)
                if isinstance(history, list):
                    player[key] = [new if room_id == old else room_id for room_id in history]
        if state_data.get("previous_room") == old:
            state_data["previous_room"] = new


def _backfill_terminal_state(state_data: dict) -> None:
    """Add terminal item, flag and interactable data missing from older saves, in place.

    Args:
        state_data: State dict to upgrade. Existing values are never overwritten.
    """
    items = state_data.setdefault("items", {})
    if "secret_key" not in items:
        try:
            default_state = json.loads(DEFAULT_GAME_STATE_PATH.read_text(encoding="utf-8"))
            default_key = default_state["items"]["secret_key"]
        except (OSError, ValueError, KeyError, TypeError):
            default_key = None
        if default_key is not None:
            items["secret_key"] = default_key

    state_data.setdefault("flags", {}).setdefault("tr4_secret_key_copied", False)

    rooms = state_data.get("rooms")
    room = rooms.get("teachers_room_4") if isinstance(rooms, dict) else None
    if isinstance(room, dict):
        room.setdefault("interactables", {}).setdefault("computer", "Nix OS computer")


def normalize_state(state_data: dict) -> None:
    """Ensure loaded state uses the current room IDs and duration schema.

    Idempotent and safe to call on fresh or legacy state. A legacy ``duration`` string becomes the full
    ``{"last_write", "value", "pause"}`` dict, falling back to ``game_state["timestamp"]`` and ``"00:00:00"``.

    Args:
        state_data: State dict, modified in place.
    """
    _migrate_room_ids(state_data)
    _backfill_terminal_state(state_data)
    game_state = state_data.setdefault("game_state", {})
    duration = game_state.get("duration")
    if isinstance(duration, dict):
        duration["last_write"] = (
            duration.get("last_write") or game_state.get("timestamp")
        )
        duration["value"] = duration.get("value") or "00:00:00"
        duration["pause"] = duration.get("pause", False)
        return

    game_state["duration"] = {
        "last_write": game_state.get("timestamp"),
        "value": duration if isinstance(duration, str) and duration else "00:00:00",
        "pause": False,
    }


def init() -> None:
    """Load the autosave (creating it from the default template if needed) into :data:`state`.

    Idempotent: if :data:`state` is already populated it is only re-normalised. Also loads the help menu once and
    stamps ``duration["last_write"]`` with the current time so time spent while the program was closed is not counted.

    Raises:
        OSError: If the default template or help data cannot be read.
        ValueError: If a JSON file is malformed.
    """
    global state
    # 1. Initialize USER_STATE_PATH from default template if missing or 0-byte
    if not USER_STATE_PATH.exists() or USER_STATE_PATH.stat().st_size == 0:
        with open(DEFAULT_GAME_STATE_PATH) as df:
            default_state = json.load(df)
        USER_STATE_PATH.write_text(json.dumps(default_state, indent=2))

    # 2. Load actual active state into memory
    if not state:
        state = json.loads(USER_STATE_PATH.read_text())

    normalize_state(state)

    if not help_commands:
        help_commands[:] = json.loads(HELP_COMMANDS_PATH.read_text(encoding="utf-8"))

    state["game_state"]["duration"]["last_write"] = datetime.now(timezone.utc).isoformat()
    return None

def auto() -> None:
    """Advance the game clocks, autosave, and trigger the exploration-to-assembly transition.

    Called once per main-loop iteration. Steps: add the time since ``last_write`` to the total duration (unless paused);
    during ``ASSEMBLY`` also advance the assembly sub-timer; write ``user_state.json`` (unless paused); finally switch
    the phase from ``EXPLORATION`` to ``ASSEMBLY`` once the workbench is ready.

    ``last_write`` is refreshed even while paused, so paused time is discarded rather than accumulated.

    Raises:
        KeyError: If the state is missing required sections.
    """
    now = datetime.now(timezone.utc).isoformat()
    duration = state["game_state"]["duration"]
    # calculate_duration truncates to whole seconds, so sub-second remainders are dropped on every tick.
    elapsed = calculate_duration(duration["last_write"], now)
    # Always advance last_write, even when paused, so paused time never counts later.
    duration["last_write"] = now

    if not duration["pause"]:
        duration["value"] = str(elapsed + parse_time_str(duration["value"]))

    if state["game_state"]["phase"] == "ASSEMBLY":
        assembly_duration = state["game_state"]["phases"]["assembly"].setdefault(
            "duration",
            {"last_write": None, "value": "00:00:00", "pause": False},
        )
        assembly_last_write = assembly_duration.get("last_write")
        # No assembly last_write yet means the phase just started: stamp it below without adding time.
        if not duration["pause"] and assembly_last_write:
            assembly_elapsed = calculate_duration(assembly_last_write, now)
            assembly_duration["value"] = str(
                assembly_elapsed
                + parse_time_str(assembly_duration.get("value") or "00:00:00")
            )
        assembly_duration["last_write"] = now

    if not duration["pause"]:
        with open(USER_STATE_PATH, "w") as a:
            json.dump(state, a, indent=4)

    # Transition happens after the save above, so the new phase is persisted on the next tick.
    if state["workbench"]["is_ready"] and state["game_state"]["phase"] == "EXPLORATION":
        state["game_state"]["phase"] = "ASSEMBLY"
        assembly_duration = state["game_state"]["phases"]["assembly"].setdefault(
            "duration",
            {"last_write": None, "value": "00:00:00", "pause": False},
        )
        assembly_duration["last_write"] = now
        state["game_state"]["phases"]["assembly"]["activated"] = True


def save(details: Any = None) -> None:
    """Write the current state to a named slot under ``data/saves`` and register it in the database.

    Requires a registered player (``state["player"]["id"]``). The slot name comes from ``details["target"]`` or, when
    absent, is generated by :func:`src.utils.generate_save_slot.next_save_slot`. It is sanitised to word characters,
    ``-`` and ``_``. An existing slot is never overwritten; the player sees a generic error instead. Feedback is
    rendered, not returned.

    Args:
        details: Parsed command details with a ``"target"`` slot name (may be ``None``), or ``None``.
    """
    from .room import render
    if not state["player"].get("id"):
        render(colorize("You have to register to save, go to the front desk", RED))
        return None

    filename = details["target"] if details else None
    if filename is None:
        filename = next_save_slot(state["player"]["name"])

    # Sanitise to a safe file name: spaces become underscores, everything except word chars and '-' is dropped
    # (also prevents path traversal).
    filename =  re.sub(r"[^\w-]", "", filename.replace(" ", "_"))
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, f"{filename}.json")

    if not os.path.exists(save_path):
        with open(save_path, "w") as s:
            json.dump(state, s, indent=4)
        create_save(filename, state["player"]["id"])
        render(colorize(f"[system] Game saved to {filename}", BRIGHT_GREEN))
        return None
    render(colorize("An unexpected error occurred", BRIGHT_RED))
    return None

def list_saves() -> None:
    """Print the logged-in player's saves with creation dates.

    Prints a hint instead if the player is not registered or has no saves.
    """
    width = int(state["terminal_width"])
    header(colorize("SAVED CHECKPOINTS", CYAN))
    user_id = state["player"].get("id")
    out()
    if not user_id:
        text = "You have to register a profile to view saves. Go to the front desk!"
        out(colorize(text.center(width), DIM))
        return None
    user_saves = get_user_saves(user_id)
    if user_saves:
        for row in user_saves:
            date = format_timestamp(row['created_at'])
            space_needed = state["terminal_width"] - len(date) - len(row["slot"])
            out(row["slot"], end=f"{' ' * space_needed}")
            out(colorize(f"{date}", DIM))
        return None

    text = "You currently have no saved slot linked to your profile"
    out(colorize(text.center(width), DIM))
    return None

def spawn() -> str:
    """Return a valid room id for the player to start in.

    Sets ``game_state["timestamp"]`` (the game start time) if it is empty. If the stored current room does not exist
    the first known room (or ``"lobby"``) is returned; ``state`` itself is not modified for the room.

    Returns:
        The room id to start in.
    """
    room_id = state["player"]["current_room"]
    if not state["game_state"]["timestamp"]:
        state["game_state"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    rooms = state["rooms"]
    player = state["player"]
    current_room = player["current_room"]
    if not isinstance(current_room, str) or current_room not in rooms:
        current_room = room_id if room_id in rooms else next(iter(rooms), "lobby")
    return current_room

def load(details: Any) -> None:
    """Replace the active state with a save slot owned by the logged-in player.

    Renders an error and leaves state untouched if the player is not registered, does not own the slot in the database,
    or the slot file is missing. On success the slot's data (including its player identity) replaces :data:`state` in
    place, is normalised, and the clock is restarted.

    Args:
        details: Parsed command details; ``details["target"]`` is the slot name, with or without ``.json``.

    Raises:
        ValueError: If the slot file is not valid JSON.
    """
    from .room import render
    slot = details["target"].removesuffix(".json")
    if not state["player"].get("id"):
        render(
            colorize(
                text="You have to register to load, go to the front desk",
                color_code=RED
            )
        )
        return None
    is_saved = get_user_save(state["player"]["id"], slot)
    if is_saved is None:
        render(
            colorize(
                text=f"You currently do not have any progress saved as '{slot}'", color_code=RED
                )
            )
        return None
    save_path = SAVE_DIR / f"{slot}.json"
    if not save_path.exists():
        render(colorize(text=f"You currently have no saved progress as '{slot}'", color_code=RED))
        return None

    with open(save_path, encoding="utf-8") as f:
        loaded = json.load(f)
    # Mutate in place: other modules hold a reference to this dict, so it must not be rebound.
    state.clear()
    state.update(loaded)
    normalize_state(state)
    state["game_state"]["duration"]["last_write"] = datetime.now(
        timezone.utc
    ).isoformat()
    render(colorize(f"Game loaded from {slot}", BRIGHT_GREEN))
    return None

def _history_back() -> None:
    """Move to the previous room in the player's visit history.

    Pops ``player["move"]`` and pushes the current room onto ``player["forward"]``. Renders an error if there is no
    history or the room no longer exists.
    """
    from .room import render

    player = state["player"]
    history = player.setdefault("move", [])
    if not history:
        render(text=colorize("You have no previous room to go back to.", RED))
        return None

    previous_room = history[-1]
    if previous_room not in state["rooms"]:
        render(text=colorize(f"Unknown destination '{previous_room}'.", RED))
        return None

    history.pop()
    player.setdefault("forward", []).append(player["current_room"])
    player["current_room"] = previous_room
    render()
    return None


def _history_forward() -> None:
    """Move forward again after going back through history.

    Mirror of :func:`_history_back`: pops ``player["forward"]`` and pushes the current room onto ``player["move"]``.
    """
    from .room import render

    player = state["player"]
    forward = player.setdefault("forward", [])
    if not forward:
        render(text=colorize("You have no forward room to go to.", color_code=RED))
        return None

    next_room = forward[-1]
    if next_room not in state["rooms"]:
        render(text=colorize(f"Unknown destination '{next_room}'.", color_code=RED))
        return None

    forward.pop()
    player.setdefault("move", []).append(player["current_room"])
    player["current_room"] = next_room
    render()
    return None


def move(details: Any) -> None:
    """Move the player by direction, adjacent room name, or history (``back``/``forward``).

    Only rooms listed in the current room's ``exits`` are reachable. A target room may be locked: ``requires`` names an
    inventory item that unlocks it, and ``restricted`` without ``requires`` can never be opened. On success the old
    room is pushed onto ``move`` history and ``forward`` history is cleared. Failures are rendered, not raised.

    Args:
        details: Parsed command details; ``details["target"]`` is the raw destination text.
    """
    from .parser import ROOM_ALIASES, resolve_room_target
    from .room import render

    destination = details["target"]
    target = resolve_room_target(destination)

    if target == "back":
        _history_back()
        return None
    if target == "forward":
        _history_forward()
        return None

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    exits = room_data["exits"]

    # Directions are looked up in the exits; a room name must be one of the exits' targets (adjacent-only travel).
    if target in ROOM_ALIASES.values():
        target_id = exits.get(target)
    else:
        target_id = target if target in exits.values() else None

    if not target_id:
        adjacent = ", ".join(sorted(set(exits.values()))) or "nowhere"
        render(text=colorize(text=f"You cannot go to {destination} from here. Adjacent: {adjacent}.", color_code=RED))
        return None

    target_data = state["rooms"].get(target_id)
    if not target_data:
        render(
            text=colorize(
                text=f"Unknown destination '{target_id}'.",
                color_code=RED
                )
            )
        return None

    requires = target_data.get("requires")
    if requires and requires not in state["player"]["inventory"]:
        render(
            text=colorize(
                text=f"The door is locked. Access requires: {requires}.",
                color_code=RED
            )
        )
        return None
    if target_data.get("restricted") and not requires:
        render(
            text=colorize(
                text="The door is locked.",
                color_code=RED
            )
        )
        return None

    state["player"].setdefault("forward", []).clear()
    state["player"]["current_room"] = target_id
    state["player"].setdefault("move", []).append(current_room)
    render()
    return None