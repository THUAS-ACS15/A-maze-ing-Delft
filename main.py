# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

# ruff: noqa: E402 
# this prevents ruff from erroring because of the below dependency check.
# it's necessary to check deps before running any of the below imports
# to ensure no crashes and correct installs

# check dependencies before start
from install_dependencies import check_dependencies
check_dependencies()

import time
import utilities.auto_color

from rooms.dispatcher import enter_room
from utilities.story_animations import play_intro
from utilities.save_gui import display_load_menu
from utilities.main_menu import display_main_menu
from utilities.scoreboard import display_scoreboard
from utilities.credits import display_credits

state = {
    "player_name": "",
    "current_room": "lobby",
    "previous_room": None,
    "time_elapsed": 0.0,
    "start_time": time.time(),
    "has_intro_played": False,
    "is_gametime_paused": False,
    "current_objective_id": 0,
    "student_id_obtained": False,
    "equinox_coins_claimed": False,
    "visited": {
        "labd2001": False,
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
    "completed": {
        "labd2001": False,
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
    global state

    while True:
        choice = display_main_menu()

        if choice == "exit":
            break

        elif choice == "credits":
            display_credits()
            continue

        elif choice in ("new game", "continue"):
            if choice == "continue":
                loaded_state = display_load_menu()
                if loaded_state is None:
                    continue
                if isinstance(loaded_state, dict):
                    state = loaded_state

            if not state["has_intro_played"]:
                state["is_gametime_paused"] = True
                play_intro()
                state["is_gametime_paused"] = False
                state["has_intro_played"] = True
            
            # keep dispatching rooms until the player actually exits,
            # so main menu doesn't take over
            current = state.get("current_room", "lobby")
            if not isinstance(current, str):
                current = "lobby"

            while current not in ("quit", "exit"):
                next_room = enter_room(current, state)
                if not isinstance(next_room, str):
                    break
                current = next_room
                state["current_room"] = current

            break
        
        elif choice == "scoreboard":
            display_scoreboard()
            continue


if __name__ == "__main__":
    main()