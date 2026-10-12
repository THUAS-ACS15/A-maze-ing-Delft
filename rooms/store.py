# -----------------------------------------------------------------------------
# File: store.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys
from random import choice

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue
from data.story_dialogue_bank import story_dialogue_bank

room_dialogue_bank = story_dialogue_bank["rooms"]["store"]

# This dict matches item name to price, so as not to neeed saving in db
item_prices = {
    "Eeyore plushie": 25,
    "Delft mug": 10,
}

def get_available_items(state: dict) -> list:
    """
    Returns a list of available items in the store.

    This function retrieves the list of available items in the store from the game state.

    Inputs:
        - state (dict): The current game state dict.

    Outputs:
        - available_items (list): A list of available items in the store, where each item is represented as a list
        containing its name, description, and price.
    """
    available_items = state["store_available_items"]

    return available_items


def check_store_completion(state: dict) -> None:
    """
    Checks if the store has been completed, i.e. if every item was bought.

    This function checks if the store has been completed by verifying if there are any
     available items left in the
    store.
    If there are no available items, it updates the game state to mark it as completed.

    Inputs:
        - state (dict): The current game state dict.

    Outputs: NONE
    """
    if len(state["store_available_items"]) == 0 and not state["completed"]["store"]:
        state["completed"]["store"] = True
        clear_screen()
        print_dialogue(room_dialogue_bank["completed"])


def enter_store(state: dict) -> str:
    """Starter function for the store."""

    state["previous_room"] = "store"

    clear_screen()
    print_dialogue(room_dialogue_bank["enter"])
    print_dialogue(room_dialogue_bank["enter_detail"])
    print_dialogue(room_dialogue_bank["enter_prompt"])

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        store. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """
        if not state["completed"]["store"]:
            print_dialogue(room_dialogue_bank["look_intro"])
            print_dialogue(room_dialogue_bank["look_detail"])
            print_dialogue(room_dialogue_bank["look_items"])
            for item in get_available_items(state):
                print(f"  - {item[0]} for €{item[1]}")
        else:
            print_dialogue(room_dialogue_bank["look_done"])
        print("- Possible exits: lobby")
        print(
            "- Your current inventory:",
            state["inventory"],
        )

    def handle_help() -> None:
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """

        print("Available commands:")
        print("- look around         : Examine the room for clues.")
        if not state["completed"]["store"]:
            print("- buy <item>          : Buy an item from the store.")
        print("- go lobby / back     : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handle_go(destination: str) -> str | None:
        """
        Handles movement out of the room.

        This function checks if the player can move to the given destination from this
         room. If the destination is valid, it returns the destination string. Otherwise,
         it prints an error message
         and returns
        None.

        Inputs:
            - destination (str): The destination the player wants to go to.

        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
        valid_destinations = ["lobby", "back"]

        if destination in valid_destinations:
            print_dialogue(room_dialogue_bank["leave"])
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_buy(item_to_buy: str) -> None:
        """
        Handles the purchase of an item from the store.

        This function checks if the item the player wants to buy is available in the store.
        If the item is available, it prompts the player for confirmation. If confirmed, it adds
        the item to the player's inventory, deducts the cost, and removes the item from the store's available items.

        Inputs:
            - item_to_buy (str): The name of the item the player wants to buy.

        Outputs: NONE
        """
        found = False
        # Random greetings chosen after confirming buy
        congratulations = [
            "Congratulations!",
            "Nice!",
            "Happy day!",
        ]
        available_items = get_available_items(state)

        # Lower input so we are sure they match
        item_to_buy = item_to_buy.lower()

        # Use enumerate so we can pop that index later
        for id, item in enumerate(available_items):
            if item[0].lower() == item_to_buy:
                found = True
                print(f"found {item[0]} id {id}")
                confirmation = input(f"Confirm purchase of €{item[1]} for {item[0].capitalize()}? (y/n) > ")

                if confirmation in [
                    "y",
                    "ye",
                    "yes",
                ]:
                    # Add item to inventory, remove cost and remove from stock
                    state["inventory"].append(item[0])
                    state["coin_balance"] -= item[1]
                    state["store_available_items"].pop(id)

                    clear_screen()

                    chosen_congratulation = choice(congratulations)
                    print(f"You bought {item[0]} for €{item[1]}. {chosen_congratulation}")
                    break
                else:
                    clear_screen()
                    print("You decide to save your finances this time.")
                    break
        if not found:
            print("No item found with that name.")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        # Check if all items were bought
        check_store_completion(state)

        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("buy "):
            item_to_buy = command[4:].strip()
            item_to_buy = item_to_buy.replace("_", " ")
            handle_buy(item_to_buy)

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)
        
        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
