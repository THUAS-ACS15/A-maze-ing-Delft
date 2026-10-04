# -----------------------------------------------------------------------------
# File: classroom_d2015.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# ANSI Color Codes (Defined here to keep the text below easy to read)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[1;95m"
RESET = "\033[0m"

# Items available to pick up in this room
room_items = [
    "high-capacity battery pack"
]

def enter_classroom_d2015(state: dict) -> str:
    """Starter function for Classroom D2.015."""

    clear_screen()
    print(f"{MAGENTA}=== CLASSROOM D 2015 ==={RESET}")
    print(f"{CYAN}You enter Classroom D2.015. Leftover student project bins are scattered everywhere.{RESET}")
    print(f"{CYAN}You spot some old circuit boards and wiring sticking out of the boxes.{RESET}")

    # Ensure inventory exists in state to avoid errors
    if "inventory" not in state:
        state["inventory"] = []

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """Describes the room and items."""
        print(f"{CYAN}You look through the messy project bins.{RESET}")
        
        if "high-capacity battery pack" in room_items:
            print(f"Inside a plastic bin, you see a heavy {GREEN}High-Capacity Battery Pack{RESET}.")
        else:
            print(f"{CYAN}The bins are mostly empty now. You already took what you needed.{RESET}")

        print(f"\n- Possible exits: {YELLOW}front desk{RESET}, {YELLOW}d2035{RESET}")
        print(f"- Your current inventory: {state['inventory']}")

    def handle_help() -> None:
        """Lists available commands."""
        print(f"{YELLOW}Available commands:{RESET}")
        print("- ?                 : Show this help message.")
        print("- look around       : Examine the room for items.")
        print("- take <item>       : Pick up a component.")
        print("- go <room>         : Move to an adjacent room.")
        print("- status            : Check your player status.")
        print("- pause / save      : Open the save menu.")
        print("- quit              : Quit the game.")

    def handle_take(item: str) -> None:
        """Handles picking up a component."""
        if item in room_items:
            room_items.remove(item)
            state["inventory"].append(item.title())
            print(f"{GREEN}>> You lug the {item.title()} into your inventory. Heavy, but necessary.{RESET}")
        else:
            print(f"{RED}❌ There's no '{item}' here to take.{RESET}")

    def handle_go(destination: str) -> str | None:
        """Handles movement out of the room."""
        if destination in ["front desk", "front_desk", "lobby", "back"]:
            print(f"{YELLOW}You head back out to the Lobby (Front Desk).{RESET}")
            state["previous_room"] = "classroomd2015"
            return "front_desk"
            
        elif destination in ["d2035", "classroom d2035"]:
            print(f"{YELLOW}You walk over to Classroom D2.035.{RESET}")
            state["previous_room"] = "classroomd2015"
            return "classroom_d2035"
            
        else:
            print(f"{RED}❌ You can't go to '{destination}' from here.{RESET}")
            return None

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input(f"\n{YELLOW}>{RESET} ").strip().lower()

        if command == "look around" or command == "look":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("take "):
            clear_screen()
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            clear_screen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)
            
        elif command in ["quit", "exit"]:
            clear_screen()
            print(f"{RED}Shutting down system. Game over.{RESET}")
            sys.exit()

        else:
            clear_screen()
            print(f"{RED}❓ Unknown command. Type '?' to see available commands.{RESET}")
