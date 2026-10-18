from .rooms.lobby import inspect_terminal
from .display_functional import clear, out
from .engine_functional import helper, inventory, prompt
from .parser_functional import parse
from .room_functional import render, get_room, look, inspect
from .rooms.lab_d_2001 import workbench as render_workbench
from .state_functional import get_current_room_id, get_room_data, get_state, set_state, \
    spawn, load_from_file, save_to_file, move_player, state
from .utils.colors import BRIGHT_GREEN, BOLD

LAST_ROOM_ID: str | None = None


def exploration() -> None:
    """Single prompt cycle; run() owns the while loop (lobby spawn)."""
    raw = prompt()
    verb, details = parse(raw)

    if verb == "UNKNOWN":
        render()
        print("I don't understand that command. Type 'help' for actions.")
        render()
    elif verb == "UNKNOWN":
        print("I don't understand that command. Type 'help' for actions.")
    elif verb == "INVALID":
        render()
        print(details.get("message", "Invalid command."))
    elif verb == "quit":
        set_state("running", False)
        print("Goodbye.")
        return
    elif verb == "help":
        helper(get_state("phase"))
        return
    elif verb == "clear":
        clear()
        render()
    elif verb == "look":
        render()
    elif verb == "inventory":
        inventory(
            get_state("inventory"), get_state("items")
        )
        return
    elif verb == "save":
        save_to_file(details.get("target", "save_slot_1.json"))
    elif verb == "load":
        if load_from_file(details.get("target", "save_slot_1.json")):
            spawn("lobby")
            _last_room_id = None
        return
    elif verb == "inspect":
        target = details.get("target", "")
        if target == "terminal" and get_state("player").get("current_room") == "lobby":
            logo, message = inspect_terminal()
            render(text=message, asset=logo)
        return
    elif verb == "go":
        render()
        target = details.get("target", "")
        ok, result = move_player(target)
        if not ok:
            print(result)
    else:
        render()
        print("Unknown command. Type 'help' for actions.")

def assembly() -> None:
    state = get_state()
    """Locked in lab_d2001 until 'activate'. Single prompt cycle."""
    if state.get("current_room") != "lab_d2001":
        state.get("player", {}).get("current_room").set("lab_d2001")
        last_room_id = state.get("move")[-1]
    if last_room_id != "lab_d_2001":
        render()
        render_workbench()

    raw = prompt()
    verb, details = parse(raw)

    if verb == "EMPTY":
        return
    if verb == "UNKNOWN":
        print("Assembly locked. Type 'activate' (or 'inspect workbench', 'help').")
        return
    if verb == "INVALID":
        print(details.get("message", "Invalid command."))
        return
    if verb == "quit":
        set_state("running", False)
        print("Goodbye.")
        return
    if verb == "help":
        helper("ASSEMBLY")
        return
    if verb == "clear":
        clear()
        return
    if verb == "look":
        look()
        return
    if verb == "inventory":
        inventory()
        return
    if verb == "save":
        save_to_file(details.get("target", "save_slot_1.json"))
        return
    if verb == "load":
        if load_from_file(details.get("target", "save_slot_1.json")):
            spawn("lobby")
            get_state("move").set([])
        return
    if verb == "go":
        print("Navigation disabled during assembly. Type 'activate' to boot the unit.")
        return
    if verb == "take":
        print("Assembly locked. All components are on the workbench. Type 'activate'.")
        return
    if verb == "use":
        print("Assembly locked. Type 'activate' to boot the unit.")
        return
    if verb == "inspect":
        target = details.get("target", "")
        if target not in ("workbench", ""):
            render_workbench()
            return
        description = inspect(target)
        out(description)
        return
    if verb == "activate":
        current = get_state("current_room")
        handler = getattr(current, "on_activate", None)
        if handler is None:
            print("Nothing to activate here.")
            return
        ok, msg = handler(state)
        print(msg)
        state.get("move").set([])
        return
    print("Assembly locked. Type 'activate'.")

def chat() -> None:
    """Finale: freeform chat via AIClient. Single prompt cycle."""
    if not getattr("_chat_booted", False):
        clear()
        out_boot_banner()
        chat_booted = True

    raw = prompt().strip()
    if not raw:
        return
    lowered = raw.lower()
    if lowered in ("quit", "exit", "q"):
        set_state("running", False)
        print("Connection closed. Goodbye.")
        return
    if lowered in ("help", "?", "h", "commands"):
        helper("CHAT")
        return
    if lowered in ("clear", "cls"):
        clear()
        return
    if lowered == "save":
        save_to_file("save_slot_1.json")
        return

    print("A-maze-ing-delft> ", end="", flush=True)
    try:
        for token in stream_response(raw):
            print(token, end="", flush=True)
        print()
    except Exception as exc:
        print(f"\n[Comms error: {exc}]")


def _out_boot_banner(self) -> None:
    out(
        self.display.colorize(
            "A-maze-ing-Delft IS ONLINE.", BRIGHT_GREEN + BOLD
        )
    )
    out(
        "You are now connected to the A-maze-ing-Delft super intelligence in Lab D 2001. Speak freely."
    )
    out("Type 'quit' to disconnect.")