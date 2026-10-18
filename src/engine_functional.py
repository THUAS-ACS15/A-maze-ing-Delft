from typing import Any

from .parser_functional import parse
from .room_functional import get_room, LAST_ROOM_ID, render
from .utils.colors import BRIGHT_CYAN, BOLD, BRIGHT_GREEN, BRIGHT_YELLOW, DIM, BRIGHT_WHITE
from .utils.commands import HELP_COMMANDS
from .display_functional import draw_line, out, colorize, clear
from .state_functional import spawn, is_running, get_phase, get_current_room_id, \
    get_state, set_state, save_to_file, load_from_file, state


def prompt() -> str:
    return input("\n> ")

def render_inventory() -> None:
    """Renders carried items and displays total core assembly parts held."""

    draw_line("─")
    out(colorize("INVENTORY", BRIGHT_CYAN + BOLD))
    draw_line("─")

    current_inventory = state["player"]["inventory"]
    if not current_inventory:
        out(colorize("Your inventory is currently empty.", DIM))
        out()
        return

    assembly_parts_count = 0
    for item in current_inventory:
        item_data = state["items"][item]
        is_part = item_data["is_assembly_part"]

        if item_data["is_assembly_part"]:
            assembly_parts_count += 1
            tag = f" {colorize('[ASSEMBLY PART]', BRIGHT_GREEN)}"
        else:
            tag = ""

        out(f" • {colorize(item_data["name"], BRIGHT_YELLOW)}{tag}")
        out(f"   {colorize(item_data["description"], DIM)}")

    out(
        colorize(
            f"\nAssembly Components Collected: {assembly_parts_count}/{len(state["workbench"]["required_parts"])}", BRIGHT_WHITE
        )
    )
    out()

def helper(phase: str = "EXPLORATION") -> None:
    if phase == "ASSEMBLY":
        HELP_COMMANDS.append(("Assembly", [
            ("activate", "Boot unit (power on, start)", "activate"),
            ("inspect workbench", "Show installed vs missing parts", "inspect workbench"),
        ]))

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

def handle_command(command: str, phase: str = "EXPLORATION") -> None:
    data = get_room()
    room_id = get_current_room_id()
    items = get_state("items")
    if LAST_ROOM_ID != room_id:
        render(room_id=room_id, room_data=data, items=items)

    raw = prompt()
    verb, details = parse(raw)

    if verb == "EMPTY":
        return
    if verb == "UNKNOWN":
        print("I don't understand that command. Type 'help' for actions.")
        return
    if verb == "INVALID":
        print(details.get("message", "Invalid command."))
        return
    if verb == "quit":
        set_state("running", False)
        print("Goodbye.")
        return
    if verb == "help":
        helper(get_state("phase"))
        return
    if verb == "clear":
        clear()
        render(room_id=room_id, room_data=data, items=items)
        return
    if verb == "look":
        render(room_id=room_id, room_data=data, items=items)
        return
    if verb == "inventory":
        render_inventory()
        return
    if verb == "save":
        save_to_file(details.get("target", "save_slot_1.json"))
        return
    if verb == "load":
        if load_from_file(details.get("target", "save_slot_1.json")):
            spawn("lobby")
            _last_room_id = None
        return


def run() -> None:
    # Imported lazily to break the engine_functional <-> phase circular import.
    from .phase import exploration, assembly, chat
    spawn("lobby")
    while is_running():
        phase = get_phase()

        if phase == "EXPLORATION":
            exploration()
        elif phase == "ASSEMBLY":
            assembly()
        elif phase == "CHAT_MODE":
            chat()
        else:
            exploration()