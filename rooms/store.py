# -----------------------------------------------------------------------------
# File: store.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

import sys
from random import choice
from utilities.clear_screen import clearScreen

def getAvailableItems(state: dict) -> list:
    """
    Returns a list of available items in the store.
    
    This function retrieves the list of available items in the store from the game state.
    
    Inputs:
        - state (dict): The current game state dict.
    
    Outputs:
        - available_items (list): A list of available items in the store, where each item is represented as a list containing its name, description, and price.
    """
    available_items = state["store_available_items"]

    return available_items

def checkStoreCompletion(state: dict) -> None:
    """
    Checks if the store has been completed, i.e. if every item was bought.

    This function checks if the store has been completed by verifying if there are any available items left in the store. 
    If there are no available items, it updates the game state to mark it as completed.

    Inputs:
        - state (dict): The current game state dict.

    Outputs: NONE
    """
    if len(state["store_available_items"]) == 0:
        state["completed"]["store"] = True

    clearScreen()
    print("Looks like you've bought everything in the store. Congratulations!")

def enterStore(state: dict) -> str:
    """Starter function for the store."""

    clearScreen()
    state["visited"]["store"] = True
    print("🏪 You enter the store.")
    print("You find some interesting items placed randomly around it.")
    print("Maybe you should check it out.")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.
        
        This function describes the room and gives clues to the player about the 
        store. It also shows the possible exits and the 
        player's current inventory.
        
        Inputs: NONE
        
        Outputs: NONE
        """
        if not state["completed"]["store"]:
            print("You take a closer look at the items in the store.")
            print("It seems like there's some interesting items here.")
            print("You see the following items:")
            for item in getAvailableItems(state):
                print(f"  - {item[0]} for €{item[1]}")
        else:
            print("You've already bought everything useful in the store. You should probably explore elsewhere.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handleHelp() -> None:
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

    def handleGo(destination: str) -> str:
        """
        Handles movement out of the room.
        
        This function checks if the player can move to the given destination from this room.
        If the destination is valid, it returns the destination string. Otherwise, it prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.
        
        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
        valid_destinations = ["lobby", "back"]
        
        if destination in valid_destinations:
            print("You decide to leave the store and return to the lobby.")
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handleBuy(item_to_buy: str) -> None:
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
        congratulations = ["Congratulations!", "Nice!", "Happy day!"]
        available_items = getAvailableItems(state)

        # Lower input so we are sure they match
        item_to_buy = item_to_buy.lower()

        # Use enumerate so we can pop that index later
        for id, item in enumerate(available_items):
            if item[0].lower() == item_to_buy:
                found = True
                print(f"found {item[0]} id {id}")
                confirmation = input(f"Confirm purchase of €{item[1]} for {item[0].capitalize()}? (y/n) > ")

                if confirmation in ["y", "ye", "yes"]:
                    # Add item to inventory, remove cost and remove from stock
                    state["inventory"].append(item[0])
                    state["coin_balance"] -= item[1]
                    state["store_available_items"].pop(id)

                    clearScreen()

                    chosen_congratulation = choice(congratulations)
                    print(f"You bought {item[0]} for €{item[1]}. {chosen_congratulation}")
                    break
                else:
                    clearScreen()
                    print("You decide to save your finances this time.")
                    break
        if not found:
            print("No item found with that name.")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        # Check if all items were bought
        checkStoreCompletion(state)

        command = input("\n> ").strip().lower()

        if command == "look around":
            clearScreen()
            handleLook()

        elif command == "?":
            clearScreen()
            handleHelp()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handleGo(destination)
            if result:
                return result

        elif command.startswith("buy "):
            item_to_buy = command[4:].strip()
            item_to_buy.replace("_", " ")
            handleBuy(item_to_buy)

        elif command == "quit":
            clearScreen()
            print("👋 You leave the store and close your eyes. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")