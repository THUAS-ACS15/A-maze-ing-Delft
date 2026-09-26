# -----------------------------------------------------------------------------
# File: dispatcher.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Single entry point for entering rooms.

Replaces the if/elif dispatch chain with a registry lookup plus the
special cases (gated Equinox room, quit/exit, unknown room names).
"""

import time

from .lobby import enterLobby
from .store import enterStore
from .lab_d2001 import enterLabD2001
from .teachersroom1 import enterTeachersRoom1
from .teachersroom2 import enterTeachersRoom2
from .project_room_1 import enterProjectRoom1
from .project_room_2 import enterProjectRoom2
from .front_desk import enterFrontDesk
from .equinox_student_society import enterEquinoxStudentSociety
from .classroom_d2015 import enterClassroomD2015
from .classroom_d2035 import enterClassroomD2035

ROOM_HANDLERS = {
    "lobby": enterLobby,
    "store": enterStore,
    "labd2001": enterLabD2001,
    "teachersroom1": enterTeachersRoom1,
    "teachersroom2": enterTeachersRoom2,
    "projectroom1": enterProjectRoom1,
    "projectroom2": enterProjectRoom2,
    "frontdesk": enterFrontDesk,
    "equinoxstudentsociety": enterEquinoxStudentSociety,
    "classroomd2015": enterClassroomD2015,
    "classroomd2035": enterClassroomD2035,
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
        print("❌ The door doesn't budge. It looks like you need to obtain a student ID to enter this room.")
        time.sleep(2.0)
        return "lobby"

    return handler(state)
