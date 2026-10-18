from typing import Any

from pip._internal.distributions import installed

from ..utils.colors import BRIGHT_MAGENTA, BOLD, BRIGHT_GREEN, RED, DIM, BRIGHT_YELLOW
from ..display_functional import out, draw_line, colorize
from ..state_functional import set_state, get_state, state


def inspect_workbench(text: str | None = None) -> None:
    """Displays workbench assembly status in Lab D 2001."""

    installed_parts = state["workbench"]["installed_parts"]
    required_parts = state["workbench"]["required_parts"]

    draw_line("═")
    out(
        colorize(
            "WORKBENCH ASSEMBLY STATUS", BRIGHT_MAGENTA + BOLD
        )
    )
    draw_line("═")
    out(f"Progress: {len(installed_parts)} / {len(required_parts)} components installed.\n")

    for part in required_parts:
        item_data = state["items"][part]

        if part in installed_parts:
            status = colorize(
                "[ INSTALLED ]", BRIGHT_GREEN + BOLD
            )
        else:
            status = colorize("[ MISSING   ]", RED + DIM)

        out(f" {status} - {item_data['name']}")

    out()
    if len(installed_parts) == len(required_parts):
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
        remaining = len(required_parts) - len(installed_parts)
        if text:
          print(text)
        out(
            colorize(
                f"Locate remaining {remaining} part(s) to complete assembly.",
                DIM
            )
        )
    return

def use_on_workbench(item: str, target: str = "workbench") -> tuple[bool, str]:
    workbench = state["workbench"]
    if target != "workbench":
        return False, f"'{target}' is not a workbench component."
    required_parts = workbench["required_parts"]
    installed_parts = workbench["installed_parts"]
    inventory = state["player"]["inventory"]

    if item not in inventory:
        return False, f"You currently do not have '{item}' in your inventory."
    if item not in required_parts:
        return False, f"'{item}' is not a workbench component."
    if item in installed_parts:
        return True, f"'{item}' is already installed."
    inventory.remove(item)
    installed_parts.append(item)

    if len(installed_parts) >= len(required_parts):
        workbench["is_ready"] = True
        state.state["game_phase"] = "ASSEMBLY"
        return True, f"{item} installed. ALL COMPONENTS INSTALLED — type 'activate'."
    return True, f"{item} installed ({len(installed_parts)}/{len(required_parts)})."

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