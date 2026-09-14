# -----------------------------------------------------------------------------
# File: clear_screen.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import os
from utilities.status_bar import updateStatusBar

def clearScreen():
    from main import state

    if os.getenv("PYCHARM_HOSTED"):
        print("\n" * 50)  # fallback for PyCharm
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
    updateStatusBar(state)