from ..utils.colors import BRIGHT_MAGENTA, BOLD, BRIGHT_GREEN, RED, DIM, BRIGHT_YELLOW
from ..display import out, draw_line, colorize
from ..state import state


def render_workbench(text: str | None = None) -> None:
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
        command = text if text else "Type 'activate' or 'power on' to start the neural link."
        out(
            colorize(
                ">> ALL CORE COMPONENTS INSTALLED <<",
                BRIGHT_GREEN + BOLD
            )
        )
        out(
            colorize(
                command,
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
    try:
        item_data = state["items"][item]
    except KeyError:
        return False, f"'{item}' is not a workbench component."

    if item not in inventory:
        return False, f"You currently do not have '{item}' in your inventory."

    if item not in required_parts:
        return False, f"'{item_data["name"]}' is not a workbench component."
    if item in installed_parts:
        return True, f"'{item_data["name"]}' is already installed."
    inventory.remove(item)
    installed_parts.append(item)

    if len(installed_parts) >= len(required_parts):
        workbench["is_ready"] = True
        state["games_state"]["game_phase"] = "ASSEMBLY"
        return True, f"{item_data["name"]} installed. ALL COMPONENTS INSTALLED — type 'activate'."
    return True, f"{item_data["name"]} installed ({len(installed_parts)}/{len(required_parts)})."


def workbench_ready() -> tuple[bool, str]:
    workbench = state["workbench"]
    if workbench.get("is_ready"):
        return True, ""
    missing = len(workbench["required_parts"]) - len(workbench["installed_parts"])
    return False, f"Assembly incomplete. {missing} part(s) missing."

def verify_wifi_password(password: str) -> bool:
    return password == state["phases"]["assembly"].get("wifi_password")

def finish_activation(name: str = "") -> str:
    robot = state["phases"]["chat"]["robot"]
    if name:
        robot["name"] = name
    state["games_state"]["game_phase"] = "CHAT"
    state["player"]["move"] = []
    return f"{robot['name'].upper()} INITIALIZED"

def ready(self) -> None:
    """Displays initialization message when assembly complete."""
    return None