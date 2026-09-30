# -----------------------------------------------------------------------------
# File: clear_screen.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import os
import sys

from utilities.status_bar import update_status_bar


def clear_screen(custom_header: str = "stuck? use \"?\" for help") -> None:
    main_module = sys.modules.get("__main__")
    state = getattr(main_module, "state", None)
    if not isinstance(state, dict):
        raise RuntimeError("The main module does not contain a game state.")

    if os.getenv("PYCHARM_HOSTED"):
        print("\n" * 50)  # fallback for PyCharm
    else:
        os.system("cls" if os.name == "nt" else "clear")
    update_status_bar(state, custom_header)
