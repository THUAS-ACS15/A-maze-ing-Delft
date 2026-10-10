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
from .classroom_d2031 import enter_classroom_d2031
from .classroom_d2035 import enter_classroom_d2035
from .corridor_east import enter_east_corridor
from .corridor_south import enter_teaching_area
from .corridor_west import enter_student_wing
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
    "classroomd2031": enter_classroom_d2031,
    "classroomd2035": enter_classroom_d2035,
    "eastcorridor": enter_east_corridor,
    "teachingarea": enter_teaching_area,
    "studentwing": enter_student_wing
}

# This dict maps room names to a certain objective ID, to ensure progression
# happens in a certain order
# Format: "room_name": (min_objective_id, reject_message)
ROOM_REQUIREMENTS = {
    # lobby is always accessible
    "lobby": (0, None),

    # corridors are unlocked when the lowest-level room connected to them is unlocked
    "eastcorridor": (2, "The East Corridor seems to be blocked off for now. You should look elsewhere."),
    "studentwing": (5, "The Student Wing seems to be blocked off for now. You should look elsewhere."),
    "teachingarea": (6, "The Teaching Area is currently closed off. You should look elsewhere."),

    # individual rooms and their requirements
    "frontdesk": (1, ("You turn around at the last moment; maybe you should take a look "
                  "around the Lobby before you head anywhere.")),
    "teachersroom1": (2, ("The door to this room doesn't budge. You should get a student" 
                      "ID, maybe you could scan it on the door.")),
    "teachersroom2": (3, "Teacher's Room 2 is occupied right now."),
    "teachersroom4": (4, "Teacher's Room 4 is currently restricted."),
    "projectroom2": (5, "Project Room 2 is reserved right now."),
    "classroomd2035": (6, "Classroom D2.035 is locked."),

    # store is inaccessible now, may be used later
    "store": (None, "The door doesn't budge. A sign on it indicates it's under maintenance."),
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
    if room_name == "mainmenu":
        return

    handler = ROOM_HANDLERS.get(room_name)
    if handler is None:
        print(f"Unknown room '{room_name}'. Returning to Lobby...")
        time.sleep(1.0)
        return "lobby"

    # +--------------------------------------------+
    # | Room checks (against items & objective ID) |
    # +--------------------------------------------+
    current_objective_id = state["current_objective_id"]

    if room_name in ROOM_REQUIREMENTS:
            min_objective, reject_message = ROOM_REQUIREMENTS[room_name]

            # check if room is completely unavailable
            if min_objective is None:
                print(f"\n{reject_message}")
                time.sleep(1.5)
                state["current_room"] = state["previous_room"]
                return state["current_room"]

            # check if player's objective ID is too low
            if current_objective_id < min_objective:
                print(f"\n❌ {reject_message}")
                time.sleep(1.5)
                state["current_room"] = state["previous_room"]
                return state["current_room"]
    
    return handler(state)
