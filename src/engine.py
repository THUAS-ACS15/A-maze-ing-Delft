from typing import Any

from .rooms.lab_d2_001 import use_on_workbench, workbench
from .rooms.teachers_room_1 import use_desk_code
from .state import auto
from .room import render
from .utils.colors import BRIGHT_CYAN, BOLD, BRIGHT_GREEN, BRIGHT_YELLOW, DIM, \
    BRIGHT_WHITE, BRIGHT_MAGENTA, RED
from .utils.commands import HELP_COMMANDS
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
    assembly_help = ("Assembly", [
            ("activate", "Boot unit (power on, start)", "activate"),
            ("inspect workbench", "Show installed vs missing parts", "inspect workbench"),
        ])

    if state["game_state"]["phase"] == "ASSEMBLY":
        HELP_COMMANDS.append(assembly_help)
    else:
        if assembly_help in HELP_COMMANDS:
            HELP_COMMANDS.remove(assembly_help)

    try:
        import os

        from rich.console import Console
        from rich.table import Table

        console = Console(highlight=False, force_terminal=None if os.getenv("NO_COLOR") else True)
        for title, rows in HELP_COMMANDS:
            table = Table(title=title, show_header=True, header_style="bold")
            table.add_column("Command", style="cyan", no_wrap=True)
            table.add_column("Description")
            table.add_column("Example", style="dim")
            for cmd, desc, ex in rows:
                table.add_row(cmd, desc, ex)
            console.print(table)
    except ModuleNotFoundError:
        out("Available Commands:")
        for title, rows in HELP_COMMANDS:
            out(f"[{title}]")
            for cmd, desc, ex in rows:
                out(f"  {cmd:<24} {desc}  e.g. {ex}")

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

def take(item: str) -> None:
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

def command(verb, details) -> None:
    if verb == "quit":
        state["running"] = False
        render("Goodbye. see you again soon")
        return
    elif verb == "help":
        helper()
        return
    elif verb == "inventory":
        inventory()
        return
    elif verb == "use":
        use(details)
    elif verb == "save":
        save(details.get("target", "save_slot_1.json"))
    elif verb == "inspect":
        inspect(details)
        return
    elif verb == "look":
        render()
        return
    elif verb == "take":
        item = details.get("target", "")
        take(item)
        return
    elif verb == "go":
        target = details.get("target", "")
        move(target)


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