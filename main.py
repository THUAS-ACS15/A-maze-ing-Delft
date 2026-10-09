# -----------------------------------------------------------------------------
# File: main.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# -----------------------------------------------------------------------------

import time

from rooms.dispatcher import enter_room
from utilities.save_gui import display_load_menu
from utilities.main_menu import display_main_menu
from utilities.scoreboard import display_scoreboard
from utilities.credits import display_credits
from utilities.story_animations import play_intro

from debug_settings import SKIP_INTRO, SKIP_MAIN_MENU_TO_NEW_GAME

state = {
    "player_name": "",
    "current_room": "labd2001",
    "time_elapsed": 0.0,
    "start_time": time.time(),
    "has_intro_played": False,
    "is_gametime_paused": False,
    "coin_balance": 0,
    "current_objective_id": 0,
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
        if SKIP_MAIN_MENU_TO_NEW_GAME:
            choice = "new game"
        else:
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

            if state["has_intro_played"] is False and not SKIP_INTRO:
                state["is_gametime_paused"] = True
                play_intro()
                state["is_gametime_paused"] = False
                state["has_intro_played"] = True

            # if skipping intro make sure to not play it after value is toggled on the same save
            if SKIP_INTRO:
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