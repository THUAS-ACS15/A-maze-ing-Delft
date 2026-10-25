import json
import copy

from typing import Any

from .model import get_user, create_user
from .rooms.lab_d2_001 import use_on_workbench, workbench
from .rooms.teachers_room_1 import use_desk_code
from .state import auto, help_commands, list_saves, load, DEFAULT_GAME_STATE_PATH
from .room import render
from .utils.colors import BRIGHT_CYAN, BOLD, BRIGHT_GREEN, BRIGHT_YELLOW, DIM, \
    BRIGHT_WHITE, BRIGHT_MAGENTA, RED
from .display import draw_line, out, colorize
from .state import spawn,  \
    save, move, state


def prompt(message: str | None = None) -> str:
    if message is None:
        return input("\n> ").strip()
    return input(f"\n{message} >").strip()

def inventory() -> None:
    """Renders carried items and displays total core assembly parts held."""

    draw_line("=")
    out(colorize(f"[{state['game_state']['phase']}]", BRIGHT_MAGENTA))
    out(colorize("INVENTORY", BRIGHT_CYAN + BOLD))
    out(colorize(f"{state['game_state']['duration']}", DIM))
    draw_line("=")

    if not state["player"]["inventory"]:
        out(colorize("Your inventory is currently empty.", DIM))
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
    groups = [
        group for group in help_commands
        if group["title"] != "Assembly" or state["game_state"]["phase"] == "ASSEMBLY"
    ]

    try:
        import os

        from rich.console import Console
        from rich.table import Table

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

def inspect(details) -> None:
    target = details["target"]
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
    else:
        render(text=colorize("The item you're trying to inspect is unavailable", color_code=RED))
        return None

def use(details: Any) -> None:
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
    item = details["target"]
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]
    if item not in room_data["items"]:
        render(text=colorize(f"There is no '{item}' here.", color_code=RED))
        return None
    room_data["items"].remove(item)
    state["player"]["inventory"].append(item)
    i = state["items"][item]
    render(colorize(f"You picked up {i['name']}", BRIGHT_GREEN))
    return None

def exit_game() -> None:
    state["running"] = False
    render("Goodbye. see you again soon")
    return None

def register(details: Any) -> None:
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
    name = details["target"]
    if not state["player"]["current_room"] == "front_desk":
        render(colorize(text="You can only register at the front desk", color_code=RED))
        return None
    if name is None:
        render(text=colorize("Please enter a name", color_code=RED))
        return None
    user = get_user(name)
    if not user:
        render(colorize(f"User '{name}' does not exist", color_code=RED))
        return None
    state["player"]["name"] = name
    state["player"]["id"] = user["id"]
    render(colorize(f"You are currently logged in as {name}", color_code=BRIGHT_GREEN))
    return None

def restart() -> None:
    snapshot = copy.deepcopy(state)
    with open(DEFAULT_GAME_STATE_PATH) as df:
        state.clear()
        state.update(json.load(df))
        state["player"]["name"] = snapshot["player"]["name"]
        state["player"]["id"] = snapshot["player"]["id"]
    render(text=colorize("New game!", color_code=BRIGHT_GREEN))


def commands(verb, details) -> None:
    if verb == "quit":
        exit_game()
        return
    if verb == "restart":
        restart()
        return
    elif verb == "help":
        helper()
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
    elif verb == "go":
        move(details)
        return


def run() -> None:
    # Imported lazily to break the engine_functional <-> phase circular import.
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