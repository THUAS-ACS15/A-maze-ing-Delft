"""Per-phase prompt cycles for the game loop.

``run()`` in :mod:`src.engine` calls exactly one of :func:`exploration`, :func:`assembly` or :func:`chat` per loop
iteration depending on ``state["game_state"]["phase"]`` (``EXPLORATION`` -> ``ASSEMBLY`` -> ``CHAT``). Each function
reads one line, parses it, clears the screen and dispatches the command; invalid input re-renders with an error.

Attributes:
    LAST_ROOM_ID: Unused placeholder kept for compatibility.
"""

from .utils.chat import respond
from .display import clear, header, out, colorize
from .engine import  prompt, commands
from .parser import parse
from .room import render
from .state import state
from .utils.colors import BRIGHT_GREEN, BRIGHT_RED, RED
from .rooms.lab_d2_001 import activate, workbench

LAST_ROOM_ID: str | None = None

def exploration() -> None:
    """Run one exploration prompt cycle.

    Reads a command, dispatches it, and prints an error for ``UNKNOWN``/``INVALID``/``EMPTY`` verbs. The caller
    (:func:`src.engine.run`) owns the loop.
    """
    raw = prompt()
    verb, details = parse(raw)
    clear()
    commands(verb, details)
    if verb in ("UNKNOWN", "INVALID", "EMPTY"):
        render(
            colorize(text="Invalid input. Please try again. type 'help' for a list of available commands.",
                     color_code=BRIGHT_RED
                     )
            )
    return


def assembly() -> None:
    """Run one assembly-phase cycle.

    On the first call after the phase starts it shows the workbench and sets ``activated`` instead of prompting. On
    later calls it reads a command, dispatches it, handles ``activate`` (which may switch the phase to ``CHAT``) and
    prints an error for unknown input.
    """
    # First assembly tick only shows the workbench intro; the prompt starts on the next loop iteration.
    if not state["game_state"]["phases"]["assembly"]["activated"]:
        clear()
        workbench(
            colorize(
                "Build your dream robot. type 'activate' to begin activation",
                BRIGHT_GREEN
                )
        )
        state["game_state"]["phases"]["assembly"]["activated"] = True
        return
    raw = prompt()
    verb, details = parse(raw)
    clear()
    commands(verb, details)
    if verb == "activate":
        activate()
    if verb in ("UNKNOWN", "INVALID", "EMPTY"):
        render(colorize("Invalid input. Please try again. type 'help' for a list of available commands.", RED))
    return

def chat() -> None:
    """Run one chat-phase cycle.

    The first call prints a welcome message and sets ``activated``. After that, a command is dispatched normally; text
    that is not a command is sent to the robot via :func:`src.utils.chat.respond` when the player is in ``lab_d2_001``
    and reported as invalid elsewhere.
    """
    if not state["game_state"]["phases"]["chat"]["activated"]:
        clear()
        render(
            colorize(f"Welcome to A-maze-ing-Delft chat mode! You can now freely talk to "
                     f"{state['game_state']['phases']['chat']['robot']['name']}", BRIGHT_GREEN)
        )
        state["game_state"]["phases"]["chat"]["activated"] = True
        return
    raw = prompt()
    verb, details = parse(raw)
    clear()
    commands(verb, details)
    # In the lab, anything that is not a game command is treated as chat with the robot.
    if verb in ("UNKNOWN", "INVALID", "EMPTY") and state["player"]["current_room"] == "lab_d2_001":
        header()
        out()
        respond(raw)
        out()
        return
    if verb in ("UNKNOWN", "INVALID", "EMPTY"):
        render(
            colorize(
                "Invalid input. Please try again. type 'help' for a list of available commands.",
                RED
                )
            )

    return