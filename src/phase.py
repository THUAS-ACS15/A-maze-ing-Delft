from .room_functional import render_chat
from .rooms.lab_d_2001 import use_on_workbench, render_workbench, workbench_ready, verify_wifi_password, finish_activation
from .rooms.teachers_room_1 import inspect_desk, use_desk_code
from .display_functional import colorize
from .rooms.lobby import inspect_terminal
from .display_functional import clear, out
from .engine_functional import helper, render_inventory, prompt
from .parser_functional import parse
from .room_functional import render,  inspect, use, take
from .state_functional import spawn, load_from_file, save_to_file, move_player, state
from .utils.colors import BRIGHT_GREEN, BOLD, RED, GREEN, BRIGHT_MAGENTA

LAST_ROOM_ID: str | None = None
CHAT_FIRST_TIME: bool = True


def exploration() -> None:
    """Single prompt cycle; run() owns the while loop (lobby spawn)."""
    raw = prompt()
    verb, details = parse(raw)

    if verb == "UNKNOWN":
        clear()
        text = colorize("I don't understand that command. Type 'help' for actions.", color_code=RED)
        render(text=text)
        return
    elif verb == "INVALID":
        clear()
        text = colorize(details.get("message", "Invalid command."), color_code=RED)
        render(text=text)
        return
    elif verb == "quit":
        state["running"] = False
        print("Goodbye.")
        return
    elif verb == "help":
        clear()
        helper(state["phase"])
        return
    elif verb == "look":
        clear()
        render()
        return
    elif verb == "inventory":
        clear()
        render_inventory()
        return
    elif verb == "save":
        save_to_file(details.get("target", "save_slot_1.json"))
    elif verb == "load":
        if load_from_file(details.get("target", "save_slot_1.json")):
            spawn("lobby")
            _last_room_id = None
        return
    elif verb == "inspect":
        clear()
        target = details.get("target", "")
        if target == "terminal" and state["player"]["current_room"] == "lobby":
            logo, message = inspect_terminal()
            render(text=message, asset=logo)
        elif target == "desk" and state["player"]["current_room"] == "teachers_room_1":
            ok, message = inspect_desk()
            if not ok:
                render(text=colorize(message, color_code=RED))
            else:
                render(text=colorize(message, color_code=GREEN))
        elif target == "workbench" and state["player"]["current_room"] == "lab_d_2001":
           clear()
           render_workbench()
        else:
            ok, message = inspect(target)
            if not ok:
                render(text=colorize(message, color_code=RED))
            else:
                render(text=colorize(message, color_code=GREEN))
        return
    elif verb == "use":
        clear()
        item = details.get("target", "")
        target = details.get("indirect")
        if state["player"]["current_room"] == "teachers_room_1":
            ok, message = use_desk_code(item, target)
            if not ok:
                render(text=colorize(message, color_code=RED))
            else:
                render(text=colorize(message, color_code=GREEN))
            return
        if state["player"]["current_room"] == "lab_d_2001":
           ok, message =  use_on_workbench(item)
           if not ok:
               render_workbench(text=colorize(message, color_code=RED))
           else:
               render_workbench(text=colorize(message, color_code=GREEN))
           return
        else:
            ok, message = use(item, target)
            if not ok:
                render(text=colorize(message, color_code=RED))
            else:
                render(text=colorize(message, color_code=GREEN))
            return
    elif verb == "take":
        clear()
        item = details.get("target", "")
        ok, message = take(item)
        if not ok:
            render(text=colorize(message, color_code=RED))
        else:
            render(text=colorize(message, color_code=GREEN))
    elif verb == "go":
        target = details.get("target", "")
        ok, message = move_player(target)
        clear()
        if not ok:
            render(text=colorize(text=message, color_code=RED))
            return
        render()

    else:
        clear()
        render(text=colorize("Unknown command. Type 'help' for actions.", RED))

def assembly() -> None:
    """Locked in lab_d2_001 until 'activate'. Single prompt cycle."""
    if state["player"]["current_room"] != "lab_d_2001":
        state["player"]["current_room"] = state["player"]["move"][-1]
        state["player"]["move"].pop()
        state["game_phase"] = "EXPLORATION"
    clear()
    render_workbench()
    raw = prompt()
    verb, details = parse(raw)

    if verb == "EMPTY":
        clear()
        render()
        return
    elif verb == "UNKNOWN":
        clear()
        render(colorize("Assembly locked. Type 'activate' (or 'inspect workbench', 'help').", RED))
        return
    elif verb == "INVALID":
        clear()
        render(colorize(details.get("message", "Invalid command."), RED))
        return
    elif verb == "quit":
        state["running"] = False
        print("Goodbye.")
        return
    elif verb == "help":
        clear()
        helper("ASSEMBLY")
        return
    elif verb == "clear":
        clear()
        return
    elif verb == "look":
        clear()
        render()
        return
    elif verb == "inventory":
        clear()
        render_inventory()
        return
    elif verb == "save":
        clear()
        save_to_file(details.get("target", "save_slot_1.json"))
        render()
        return
    elif verb == "load":
        if load_from_file(details.get("target", "save_slot_1.json")):
            spawn("lobby")
            state["player"]["move"] = []
        return
    elif verb == "go":
        print("Navigation disabled during assembly. Type 'activate' to boot the unit.")
        return
    elif verb == "take":
        print("Assembly locked. All components are on the workbench. Type 'activate'.")
        return
    elif verb == "use":
        print("Assembly locked. Type 'activate' to boot the unit.")
        return
    elif verb == "inspect":
        target = details.get("target", "")
        if target not in ("workbench", ""):
            render_workbench()
            return
        description = inspect(target)
        print(description)
        return
    elif verb == "activate":
        ok, msg = workbench_ready()
        if not ok:
            clear()
            render(text=colorize(msg, color_code=RED))
            return
        clear()
        render_workbench(text="Enter wifi password to continue.")
        password = prompt()
        if not verify_wifi_password(password):
            clear()
            render_workbench(text="Incorrect wifi password.")
            return
        clear()
        render_workbench(text=f"Give your robot a name. Default name is {state["phases"]["chat"]["robot"]["name"]}.")
        name = prompt()
        clear()
        render_workbench(text=colorize(finish_activation(name), color_code=BRIGHT_MAGENTA))
    else:
        clear()
        render_workbench(text=colorize("Unknown command. Type 'help' for actions.", RED))
        return

def chat() -> None:
    """Finale: freeform chat via AIClient. Single prompt cycle."""
    global CHAT_FIRST_TIME
    if CHAT_FIRST_TIME:
        clear()
        render_chat("Render a helpful message congratulating the user on completing the game and a welcome message(welcome to chat mode.")
        CHAT_FIRST_TIME = False
    raw = prompt().strip()
    if not raw:
        return
    lowered = raw.lower()
    if lowered in ("quit", "exit", "q"):
        state["running"] = False
        print("Connection closed. Goodbye.")
        return
    if lowered in ("help", "?", "h", "commands"):
        helper()
        return
    if lowered in ("clear", "cls"):
        clear()
        return
    if lowered == "save":
        save_to_file("save_slot_1.json")
        return
    clear()
    render_chat(raw)


def out_boot_banner(self) -> None:
    out(
        self.display.colorize(
            "A-maze-ing-Delft IS ONLINE.", BRIGHT_GREEN + BOLD
        )
    )
    out(
        "You are now connected to the A-maze-ing-Delft super intelligence in Lab D 2001. Speak freely."
    )
    out("Type 'quit' to disconnect.")