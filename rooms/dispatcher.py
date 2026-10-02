# -----------------------------------------------------------------------------
# File: dispatcher.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Contributors: Gift Odigwe
# Date: September 2026
# -----------------------------------------------------------------------------
"""
Single entry point for entering rooms.

Replaces the if/elif dispatch chain with a registry lookup plus the
special cases (gated Equinox room, quit/exit, unknown room names).
"""

import time

from .classroom_d2015 import enter_classroom_d2015
from .classroom_d2035 import enter_classroom_d2035
from .equinox_student_society import enter_equinox_student_society
from .front_desk import enter_front_desk
from .lab_d2001 import enter_lab_d2001
from .lobby import enter_lobby
from .project_room_1 import enter_project_room1
from .project_room_2 import enter_project_room2
from .store import enter_store
from .teachersroom1 import enter_teachers_room1
from .teachersroom2 import enter_teachers_room2
from .teachersroom4 import enter_teachers_room4

ROOM_HANDLERS = {
    "lobby": enter_lobby,
    "store": enter_store,
    "labd2001": enter_lab_d2001,
    "teachersroom1": enter_teachers_room1,
    "teachersroom2": enter_teachers_room2,
    "teachersroom4": enter_teachers_room4,
    "projectroom1": enter_project_room1,
    "projectroom2": enter_project_room2,
    "frontdesk": enter_front_desk,
    "equinoxstudentsociety": enter_equinox_student_society,
    "classroomd2015": enter_classroom_d2015,
    "classroomd2035": enter_classroom_d2035,
}


def enter_room(room_name: str, state: dict):
    """Run one room visit and return the next room name.

    Inputs:
        - room_name (str): the room to enter ("quit"/"exit" leaves the game)
        - state (dict): the game state, passed through to the room handler

    Outputs:
        - str: the next room name ("quit"/"exit" means the player is leaving)
    """
    if room_name in ("quit", "exit"):
        print("Exiting... goodbye and thanks for playing!")
        return room_name

    handler = ROOM_HANDLERS.get(room_name)
    if handler is None:
        print(f"Unknown room '{room_name}'. Returning to Lobby...")
        time.sleep(1.0)
        return "lobby"

    if room_name == "equinoxstudentsociety" and not state.get("student_id_obtained"):
        print("❌ The door doesn't budge. It looks like you need to obtain a student ID " "to enter this room.")
        time.sleep(2.0)
        return "lobby"

    return handler(state)
