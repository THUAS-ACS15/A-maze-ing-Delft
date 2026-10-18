from typing import Any

from ..utils.colors import BRIGHT_MAGENTA, BOLD, BRIGHT_GREEN, RED, DIM, BRIGHT_YELLOW
from ..display_functional import out, draw_line, colorize
from ..state_functional import set_state, get_state


def workbench(workbench_data: dict[str, Any] | None = None,
                     items: dict[str, Any] | None = None) -> None:
    """Displays workbench assembly status in Lab D 2001."""
    if workbench_data is None:
        workbench_data = get_state("workbench")

    if items is None:
        items = get_state("inventory")

    installed = workbench_data.setdefault("installed_parts", [])
    required = workbench_data.setdefault("required_parts", [])

    draw_line("═")
    out(
        colorize(
            "WORKBENCH ASSEMBLY STATUS", BRIGHT_MAGENTA + BOLD
        )
    )
    draw_line("═")
    out(f"Progress: {len(installed)} / {len(required)} components installed.\n")

    for part_id in required:
        item_data = items.get(part_id, {})
        part_name = item_data.get("name", part_id)

        if part_id in installed:
            status = colorize(
                "[ INSTALLED ]", BRIGHT_GREEN + BOLD
            )
        else:
            status = colorize("[ MISSING   ]", RED + DIM)

        out(f" {status} - {part_name}")

    out()
    if len(installed) == len(required):
        out(
            colorize(
                ">> ALL CORE COMPONENTS INSTALLED <<",
                BRIGHT_GREEN + BOLD
            )
        )
        out(
            colorize(
                "Type 'activate' or 'power on' to start the neural link.",
                BRIGHT_YELLOW
            )
        )
    else:
        remaining = len(required) - len(installed)
        out(
            colorize(
                f"Locate remaining {remaining} part(s) to complete assembly.",
                DIM
            )
        )
    out()

def use(item_id: str, target: str | None, state) -> tuple[bool, str]:
    if target != "workbench":
        return  use(item_id, target, state)
    wb = set_state("workbench", {})
    required = wb().setdefault("required_parts", [])
    installed = wb().setdefault("installed_parts", [])
    set_state("player", {})
    inventory = set_state("inventory", [])

    if item_id not in inventory:
        return False, f"You are not carrying '{item_id}'."
    if item_id not in required:
        return False, f"'{item_id}' is not a workbench component."
    if item_id in installed:
        return False, f"'{item_id}' is already installed."
    inventory.remove(item_id)
    installed.append(item_id)
    if len(installed) >= len(required) and required:
        wb["is_ready"] = True
        state.state["game_phase"] = "ASSEMBLY"
        return True, f"{item_id} installed. ALL COMPONENTS INSTALLED — type 'activate'."
    return True, f"{item_id} installed ({len(installed)}/{len(required)})."

def on_activate(state) -> tuple[bool, str]:
    wb = get_state("workbench")
    if not wb().get("is_ready"):
        missing = len(wb.get("required_parts", [])) - len(wb.get("installed_parts", []))
        return False, f"Assembly incomplete. {missing} part(s) missing."
    state.state["game_phase"] = "CHAT_MODE"
    state.state.setdefault("flags", {})["lab_power_on"] = True
    return True, "A-maze-ing-Delft IS READY FOR INITIALIZATION."

def ready(self) -> None:
    """Displays initialization message when assembly complete."""
    return None