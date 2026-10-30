# -----------------------------------------------------------------------------
# File: clear_screen.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

"""Cross-platform terminal clearing with an optional status-bar refresh."""

import os
import sys

from utilities.status_bar import update_status_bar


def clear_screen(
        header_message: str = "stuck? use \"quit\" to quit or \"?\" for help",
        run_status_bar_update: bool = True
) -> None:
    """Clears the console screen and optionally updates the status bar with a header message.

    This function clears the screen by executing either cls on Windows or clear on Unix systems.
    As a fallback for PyCharm, it prints 50 newlines instead of clearing the screen.
    Additionally, it retrieves the current game state from the __main__ module and updates the status bar if needed.

    Args:
        header_message: The message to display in the status bar header after clearing
            the screen.
        run_status_bar_update: Whether to update the status bar as well. Defaults to
            True.
    """
    main_module = sys.modules.get("__main__")
    state = getattr(main_module, "state", None) if main_module is not None else None

    if os.getenv("PYCHARM_HOSTED"):
        print("\n" * 50)  # fallback for PyCharm
    else:
        os.system("cls" if os.name == "nt" else "clear")
    if run_status_bar_update and state is not None:
        update_status_bar(state, header_message)
