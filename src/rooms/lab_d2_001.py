import time

from ..room import render
from ..utils.colors import BRIGHT_MAGENTA, BOLD, BRIGHT_GREEN, RED, DIM, BRIGHT_YELLOW
from ..display import out, draw_line, colorize, clear
from ..state import state


def workbench(text: str | None = None) -> None:
    """Displays workbench assembly status in Lab D 2001."""

    installed_parts = state["workbench"]["installed_parts"]
    required_parts = state["workbench"]["required_parts"]

    draw_line("═")
    out(
        colorize(
            f"[{state['game_state']['phase']}]", BRIGHT_YELLOW
        )
    )
    out(
        colorize(
            "Lab D 2001 WORKBENCH", BRIGHT_MAGENTA + BOLD
        )
    )
    out(
        colorize(
            f"[{state['game_state']['duration']['value']}]", DIM
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
    if len(installed_parts) == len(required_parts) and state["game_state"]["phase"] != "CHAT":
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

def use_on_workbench(item: str) -> None:
    wb = state["workbench"]
    required_parts = wb["required_parts"]
    installed_parts = wb["installed_parts"]
    inventory = state["player"]["inventory"]
    try:
        item_data = state["items"][item]
    except KeyError:
        workbench(text=colorize(f"'{item}' is not a workbench component.", color_code=RED))
        return None

    if item not in state["player"]["inventory"]:
        workbench(
            text=colorize(f"You currently do not have {item_data['name']} in your inventory.", color_code=RED)
            )
        return None

    if item not in required_parts:
        workbench(
            text=colorize(
                f"'{item_data['name']}' is not a workbench component.", color_code=RED
                )
        )
        return None
    if item in installed_parts:
        workbench(
            text=colorize(
                f"'{item_data['name']}' is already installed.", color_code=RED
            )
        )
        return None
    inventory.remove(item)
    installed_parts.append(item)

    if len(installed_parts) >= len(required_parts):
        wb["is_ready"] = True
        state["game_state"]["phase"] = "ASSEMBLY"
        workbench(
            text=colorize(
                f"{item_data['name']} installed. ALL COMPONENTS INSTALLED — type 'activate'.", color_code=RED
            )
        )
        return None
    workbench(
        text=colorize(
            f"{item_data['name']} installed ({len(installed_parts)}/{len(required_parts)}).",
            color_code=RED
        )
    )
    return None

def activate() -> None:
    from ..engine import prompt

    required_parts = state["workbench"]["required_parts"]
    installed_parts = state["workbench"]["installed_parts"]
    missing = len(required_parts) - len(installed_parts)
    if missing > 0:
        workbench(colorize(f"Assembly incomplete. {missing} part(s) missing.", RED))
        return None
    workbench(text="Enter wifi password to continue.")
    password = prompt()
    clear()
    if password != state["game_state"]["phases"]["assembly"]["wifi_password"]:
        workbench(colorize("Invalid wifi credentials.", RED))
        return None
    workbench(
        text=f"Give your robot a name. Default name is {state['game_state']['phases']['chat']['robot']['name']}."
        )
    name = prompt()

    robot = state["game_state"]["phases"]["chat"]["robot"]
    if name and name.strip():
        robot["name"] = name.strip()
    clear()
    render(colorize(f"INITIALIZING {robot['name'].upper()}...", BRIGHT_GREEN))
    time.sleep(2)
    state["game_state"]["phase"] = "CHAT"
    return None