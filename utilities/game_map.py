# -----------------------------------------------------------------------------
# File: game_map.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

# ^ disable ruff checking long lines, as the map is too big on some lines

import time

from rich.align import Align
from rich.console import Console

from utilities.clear_screen import clear_screen
from utilities.main_menu import read_key
from utilities.status_bar import display_top_bar, update_status_bar

# this maps room IDs to their name on the map
# these are shortened for space
map_room_names = {
    "equinoxstudentsociety": "Equinox",
    "eastcorridor": "East Corridor",
    "studentwing": "Student Wing",
    "teachingarea": "Teaching Area",
    "labd2001": "Lab D2.001",
    "store": "Store",
    "projectroom2": "PRoom 2",
    "projectroom1": "PRoom 1",
    "lobby": "Lobby",
    "frontdesk": "Front Desk",
    "teachersroom1": "TRoom 1",
    "teachersroom2": "TRoom 2",
    "teachersroom4": "TRoom 4",
    "classroomd2015": "Class D2.015",
    "classroomd2031": "Class D2.031",
    "classroomd2035": "Class D2.035"
}

# widths maps each room id to its width.
# this makes sure the boxes on the map
# align and form a coherent visual
widths = {
    "equinoxstudentsociety": 12,
    "eastcorridor": 30,
    "studentwing": 24,
    "teachingarea": 42,
    "labd2001": 12,
    "store": 12,
    "projectroom2": 12,
    "projectroom1": 12,
    "lobby": 20,
    "frontdesk": 12,
    "teachersroom1": 12,
    "teachersroom2": 12,
    "teachersroom4": 12,
    "classroomd2015": 12,
    "classroomd2031": 12,
    "classroomd2035": 12
}

def form_map_object(state: dict) -> str:
    visited_state = state["visited"]
    if isinstance(visited_state, dict):
        visited_rooms = {
            roomid for roomid, visited in visited_state.items() if visited
        }
    else:
        visited_rooms = set(visited_state)

    # this var name is shortened so the map text below is more readable
    # d just maps the room id to what shows on the map. so "???" if it's not
    # explored, its name in yellow if it hasn't been completed,
    # or green if completed
    d = {}
    for roomid, name in map_room_names.items():
        if roomid in ["lobby", "eastcorridor", "studentwing", "teachingarea"]:
            text = name
            color = "white"
        elif roomid not in visited_rooms:
            text = "???"
            color = "red"
        else:
            text = name
            # Current room is green, other visited rooms are yellow
            if state["completed"][roomid]:
                color = "green"
            else:
                color = "yellow"
        
        # using the ^ operator we center this text to a max of widths[roomid]
        # (this also adds spaces to make everything fit inside the box bounds on the map)
        centered_text = f"{text:^{widths[roomid]}}"
        # finally, add colours to the text
        d[roomid] = f"[{color}]{centered_text}[/{color}]"

    map_object = f"""    
                     ┌────────────┐ ┌────────────┐   ┌────────────┐       ┌────────────┐ ┌────────────┐
                     │{d['labd2001']}│ │{d['store']}│   │{d['frontdesk']}│       │{d['teachersroom1']}│ │{d['teachersroom2']}│
                     └────────────┘ └────────────┘   └────────────┘       └────────────┘ └────────────┘
                            │             │                │                     │             │       
        ┌────────────┐ ┌────────────────────────┐ ┌────────────────────┐ ┌──────────────────────────────┐
        │{d['equinoxstudentsociety']}│─│{d['studentwing']}│─│{d['lobby']}│─│{d['eastcorridor']}│
        └────────────┘ └────────────────────────┘ └────────────────────┘ └──────────────────────────────┘
                               │             │               │                                    │    
                        ┌────────────┐ ┌────────────┐        │                             ┌────────────┐
                        │{d['projectroom2']}│ │{d['projectroom1']}│        │                             │{d['teachersroom4']}│
                        └────────────┘ └────────────┘        │                             └────────────┘
                                                             │                                         
                                                             │  ┌──────────────────────────────────────────┐
                                                             └──│{d['teachingarea']}│
                                                                └──────────────────────────────────────────┘
                                                                       │              │              │    
                                                                ┌────────────┐ ┌────────────┐ ┌────────────┐
                                                                │{d['classroomd2015']}│ │{d['classroomd2031']}│ │{d['classroomd2035']}│
                                                                └────────────┘ └────────────┘ └────────────┘"""
    
    return map_object

def print_map(state: dict, console: Console) -> None:
    clear_screen("", False)
    display_top_bar(console)

    # get some info to print in the header
    percent_visited = (sum(state["visited"].values()) / len(map_room_names)) * 100
    percent_completed = (sum(state["completed"].values()) / len(map_room_names)) * 100
    current_room_name = map_room_names.get(state["current_room"], 'Unknown')

    # header with some info on percents
    console.print(Align.center("Map of THUAS Delft", style = "bold white"))
    console.print(Align.center(f"Visited: {percent_visited}% | Completed: {percent_completed}% | Time paused"))
    console.print(Align.center(f"You are currently in {current_room_name}"))

    # print map
    map_object = form_map_object(state)

    console.print(map_object)
    console.print(Align.center('\n[italic]\\[use enter to exit][/italic]'))

def display_map(state: dict) -> None:
    console = Console()
    clear_screen("", False)

    enter_time = time.time()
    print_map(state, console)

    while True:
        key = read_key()

        if key == 'enter':
            # exclude time spent in map from game time
            start_time = state.get("start_time", None)
            if isinstance(start_time, (int, float)) and not isinstance(start_time, bool):
                state["start_time"] = start_time + (time.time() - enter_time)
            state["is_gametime_paused"] = False
            clear_screen('', False)
            update_status_bar(state)
            break
        else:
            print_map(state, console)