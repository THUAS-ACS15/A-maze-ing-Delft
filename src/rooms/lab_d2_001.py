"""Lab D 2001: the workbench where the robot is assembled and activated.

Installing every required part flips the phase to ``ASSEMBLY``; :func:`activate` then asks for the Wi-Fi password and
a robot name, records the player's score on the scoreboard and switches the game to the ``CHAT`` phase.
"""

import time

from ..model import create_scoreboard_entry
from ..room import render
from ..utils.colors import BRIGHT_MAGENTA, BOLD, BRIGHT_GREEN, RED, DIM, BRIGHT_YELLOW
from ..utils.parse_time import parse_time_str
from ..utils.score import calculate_score
from ..display import out, draw_line, colorize, clear
from ..state import state


def workbench(text: str | None = None) -> None:
    """Display the workbench: installed vs. missing parts and what to do next.

    Args:
        text: Optional message shown under the part list (feedback from the last action, or a custom activation hint
            once all parts are installed).
    """
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
    """Install an inventory item on the workbench.

    Rejects unknown items, items not carried, non-components and already installed parts, re-showing the workbench with
    an error. Installing the last required part sets ``workbench["is_ready"]`` and moves the phase to ``ASSEMBLY``.

    Args:
        item: Item id the player wants to install.
    """
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

    # Last part installed: the workbench is ready and the phase advances immediately.
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
    """Run the activation sequence once all parts are installed.

    Asks for the Wi-Fi password and a robot name, and records a scoreboard row if the player is registered. Phase is
    set to ``CHAT`` only after a correct password; a wrong password or missing parts just re-renders the workbench.
    Blocks for two seconds during the "initialising" splash.
    """
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

    user_id = state["player"].get("id")
    if user_id:
        total = parse_time_str(state["game_state"]["duration"]["value"])
        assembly = parse_time_str(
            state["game_state"]["phases"]["assembly"]["duration"]["value"]
        )
        # The total clock runs through both phases, so exploration time is whatever the assembly timer excludes.
        exploration = total - assembly
        # Guard against division by zero when computing the average time per room.
        room_count = len(state["rooms"]) or 1

        create_scoreboard_entry(
            user_id=user_id,
            score=calculate_score(exploration, assembly),
            avg_room_time=str(exploration / room_count),
            exploration_time=str(exploration),
            assembly_time=str(assembly),
        )

    robot = state["game_state"]["phases"]["chat"]["robot"]
    if name and name.strip():
        robot["name"] = name.strip()
    clear()
    render(colorize(f"INITIALIZING {robot['name'].upper()}...", BRIGHT_GREEN))
    time.sleep(2)
    state["game_state"]["phase"] = "CHAT"
    return None