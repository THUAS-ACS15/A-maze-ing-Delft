from .utils.chat import respond
from .display import clear, header, out, colorize
from .engine import  prompt, command
from .parser import parse
from .room import render
from .state import state
from .utils.colors import BRIGHT_GREEN, BRIGHT_RED, RED
from .rooms.lab_d2_001 import activate, workbench

LAST_ROOM_ID: str | None = None

def exploration() -> None:
    """Single prompt cycle; run() owns the while loop (lobby spawn)."""
    raw = prompt()
    verb, details = parse(raw)
    clear()
    command(verb, details)
    if verb in ("UNKNOWN", "INVALID", "EMPTY"):
        render(
            colorize(text="Invalid input. Please try again. type 'help' for a list of available commands.",
                     color_code=BRIGHT_RED
                     )
            )
    return


def assembly() -> None:
    """Locked in lab_d2_001 until 'activate'. Single prompt cycle."""
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
    command(verb, details)
    if verb == "activate":
        activate()
    if verb in ("UNKNOWN", "INVALID", "EMPTY"):
        render(colorize("Invalid input. Please try again. type 'help' for a list of available commands.", RED))
    return

def chat() -> None:
    """Finale: freeform chat via AIClient. Single prompt cycle."""
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
    command(verb, details)
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