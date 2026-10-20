from .state import auto_save
from .parser import parse
from .room import  render
from .utils.colors import BRIGHT_CYAN, BOLD, BRIGHT_GREEN, BRIGHT_YELLOW, DIM, BRIGHT_WHITE
from .utils.commands import HELP_COMMANDS
from .display import draw_line, out, colorize, clear
from .state import spawn,  \
    save_to_file, load_from_file, state


def prompt(message: str | None = None) -> str:
    if message is None:
        return input("\n> ").strip()
    return input(f"\n{message} >").strip()

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

def helper(phase: str | None = None) -> None:
    if phase is None:
        phase = state["game_state"]["game_phase"]
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
    rooms = state["rooms"]
    current_room = state["player"]["current_room"]
    items = state["items"]
    if state["player"]["move"][-1] != current_room:
        render()

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
        state["running"] = False
        print("Goodbye.")
        return
    if verb == "help":
        helper(state["phase"])
        return
    if verb == "clear":
        clear()
        render()
        return
    if verb == "look":
        render()
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
    spawn()
    while state["running"]:
        auto_save()
        if state["game_state"]["game_phase"] == "EXPLORATION":
            exploration()
        elif state["game_state"]["game_phase"] == "ASSEMBLY":
            assembly()
        elif state["game_state"]["game_phase"] == "CHAT":
            chat()
        else:
            exploration()