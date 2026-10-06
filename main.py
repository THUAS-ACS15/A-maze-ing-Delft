# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

import time

from src import Engine, StateManager
from utilities.main_menu import display_main_menu, select_save_slot
from utilities.credits import display_credits

# This module-level "state" is read directly by utilities/clear_screen.py and
# utilities/status_bar.py (via sys.modules["__main__"].state) to draw the status
# bar, so it must exist before the main menu is first shown. It is kept in sync
# with whichever save slot the player picks, separately from the StateManager
# used by the Engine for actual gameplay.
state = {
    "current_room": "lobby",
    "time_elapsed": 0.0,
    "start_time": time.time(),
    "is_gametime_paused": False,
    "coin_balance": 0,
    "student_id_obtained": False,
    "equinox_coins_claimed": False,
    "store_available_items": ["Eeyore plushie", "Delft mug"],
    "completed": {
        "labd2001": False,
        "store": False,
        "projectroom1": False,
        "projectroom2": False,
        "teachersroom1": False,
        "teachersroom2": False,
        "teachersroom4": False,
        "frontdesk": False,
        "equinoxstudentsociety": False,
        "classroomd2015": False,
        "classroomd2031": False,
        "classroomd2035": False,
    },
    "accessible": {
        "labd2001": False,
        "store": False,
        "projectroom1": False,
        "projectroom2": False,
        "teachersroom1": False,
        "teachersroom2": False,
        "teachersroom4": False,
        "frontdesk": False,
        "equinoxstudentsociety": False,
        "classroomd2015": False,
        "classroomd2031": False,
        "classroomd2035": False,
    },
    "inventory": [],
}


def main() -> None:
    """
    Entry point of the game.

    Shows the main menu in a loop. NEW GAME and CONTINUE both go through a
    save-slot selection screen first, then start the Engine with the right
    state. CREDITS shows the credits and returns to the menu. EXIT stops
    the loop. Picking "BACK" on the slot screen also returns to the menu.

    Inputs: NONE

    Outputs: NONE
    """

    while True:
        choice = display_main_menu()

        if choice == "exit":
            break

        elif choice == "credits":
            display_credits()
            continue

        elif choice == "new game":
            slot = select_save_slot("new game")
            if slot is None:
                continue

            state_manager = StateManager()
            state_manager.save_to_file(f"save_slot_{slot}.json")

        elif choice == "continue":
            slot = select_save_slot("continue")
            if slot is None:
                continue

            state_manager = StateManager()
            loaded = state_manager.load_from_file(f"save_slot_{slot}.json")
            if not loaded:
                continue

        else:
            continue

        engine = Engine(state_manager)
        engine.run()
        break


if __name__ == "__main__":
    main()