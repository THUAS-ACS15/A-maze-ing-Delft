# -----------------------------------------------------------------------------
# File: classroom_d2015.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand
# -----------------------------------------------------------------------------

import sys
from time import sleep
from utilities.animations import showActivityAnimation
from utilities.clear_screen import clearScreen

# Loose components lying on the antistatic mat, which the player can take.
bench_items = ["usb cable", "resistor", "multimeter"]

# The two answers the player has to work out from the BODMAS clues:
#   lab notebook : 12 - 2 * 4 + 6  -> 12 - 8 + 6 -> 10
#   rover sticker: (40 + 20) / 2   -> 60 / 2     -> 30
CORRECT_VOLTAGE = 10
CORRECT_FREQUENCY = 30

# Reward for getting the rover across the test track.
ROVER_REWARD = 50


def enterClassroomD2015(state: dict) -> str:
    """Starter function for Classroom D2.015."""

    clearScreen()
    state["visited"]["classroomd2015"] = True
    print("🤖 You enter Classroom D2.015, the embedded systems lab.")
    print("A marked test track takes up the middle of the floor, and a small robot rover")
    print("sits dead in the middle of it. Its status LED is off.")
    print("Along the east wall, a workbench hums with test equipment.")
    print("Maybe you should check it out.")

    # The rover puzzle has two stages, and both have to be solved in order.
    # These are kept inside the state dict so the progress survives if the
    # player walks out to the Lobby and comes back later.
    if "d2015_progress" not in state:
        state["d2015_progress"] = {
            "power_set": False,
            "rover_calibrated": False
        }

    progress = state["d2015_progress"]

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printBenchStatus() -> None:
        """
        Helper function to print the current state of the rover puzzle.

        This function shows whether the bench power supply has been set and
        whether the rover's infrared sensor has been calibrated, so the player
        always knows which of the two steps is still missing.

        Inputs: NONE

        Outputs: NONE
        """

        if progress["power_set"]:
            print("    - Bench supply : ⚡ energised, track rails are live.")
        else:
            print("    - Bench supply : 🔌 idle, the track rails are dead.")

        if progress["rover_calibrated"]:
            print("    - Rover IR link: 📡 synced.")
        else:
            print("    - Rover IR link: 📴 no carrier frequency set.")

    def roverPuzzleCheck() -> bool:
        """
        Checks if both halves of the rover puzzle are solved.

        The rover can only drive if the track rails are powered AND the infrared
        sensor is calibrated to the right carrier frequency.

        Inputs: NONE

        Outputs:
            - bool: True if the rover is ready to run, False otherwise.
        """

        if progress["power_set"] and progress["rover_calibrated"]:
            return True
        else:
            return False

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.

        This function describes the lab, prints the two BODMAS clues (the lab
        notebook on the bench and the sticker on the rover chassis) and shows
        how far the player has got. It also shows the exits and the inventory.

        Inputs: NONE

        Outputs: NONE
        """

        if not state["completed"]["classroomd2015"]:
            print("You take a closer look at the workbench.")
            print("A lab notebook is open at a page headed 'BENCH SUPPLY CALCULATION':")
            print("    \"Set line voltage to:  12 - 2 * 4 + 6\"")
            print("")
            print("You crouch by the rover. A sticker on its chassis reads:")
            print("    \"IR CARRIER FREQUENCY:  (40 + 20) / 2 kHz\"")
            print("")
            print("Its little screen blinks: 'OFFLINE - needs power and calibration.'")
            printBenchStatus()

            if bench_items:
                print("Loose on the antistatic mat:", ", ".join(bench_items))
            else:
                print("The antistatic mat is bare.")
        else:
            print("The rover is parked on its charging pad with a solid green LED.")
            print("It has already finished its run. There's nothing more to do here.")

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
        print("- look around         : Examine the bench, the notebook and the rover.")
        if not state["completed"]["classroomd2015"]:
            print("- set power           : Dial a voltage into the bench supply.")
            print("- calibrate rover     : Send an IR carrier frequency to the rover.")
            print("- start rover         : Run the rover, once power and IR are both set.")
        print("- take <item>         : Pick up a component from the workbench.")
        print("- go lobby / back     : Leave the lab and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handleTake(item: str) -> None:
        """
        Handles picking up a component from the workbench.

        This function checks whether the named component is still on the mat. If
        it is, the component is moved into the player's inventory.

        Inputs:
            - item (str): The name of the component the player wants to take.

        Outputs: NONE
        """

        if item in bench_items:
            bench_items.remove(item)
            state["inventory"].append(item)
            print(f"You pocket the {item}.")
        else:
            print(f"❌ There's no '{item}' on the workbench.")

    def handleGo(destination: str) -> str:
        """
        Handles movement out of the room.

        This function checks if the player can move to the given destination from
        this room. If the destination is valid it returns the destination string,
        otherwise it prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.

        Outputs:
            - location (str): "lobby" if valid, None otherwise.
        """

        valid_destinations = ["lobby", "back"]

        if destination in valid_destinations:
            print("You pull the lab door shut behind you and head back to the Lobby.")
            state["previous_room"] = "classroomd2015"
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handleSetPower() -> None:
        """
        Handles the first half of the puzzle: the bench power supply.

        This function asks the player for a voltage and compares it to the answer
        of the BODMAS sum in the lab notebook. A correct answer energises the
        track rails, a wrong one prints the sum again as a hint.

        Inputs: NONE

        Outputs: NONE
        """

        clearScreen()
        print("You grab the dial on the bench supply.")
        print("Notebook clue: 12 - 2 * 4 + 6")

        voltage = input("\nTarget voltage in volts > ").strip()

        # Reject anything that isn't a plain number before comparing
        if not voltage.isnumeric():
            print("The dial only takes whole volts. Try a number.")
            return

        if int(voltage) == CORRECT_VOLTAGE:
            progress["power_set"] = True
            print(f"\nClick-turn. The supply settles on {CORRECT_VOLTAGE}V and the rails hum.")
            print("A row of green LEDs runs down the edge of the test track.")
        else:
            print(f"\nBZZT! {voltage}V trips the bench breaker instantly.")
            print("Remember the order of operations: multiplication before subtraction.")

    def handleCalibrateRover() -> None:
        """
        Handles the second half of the puzzle: the infrared carrier frequency.

        This function asks the player for a frequency in kHz and compares it to
        the answer of the sum on the rover's chassis sticker. The rover refuses
        to listen at all if the track rails have not been powered first.

        Inputs: NONE

        Outputs: NONE
        """

        clearScreen()

        # The rover is bus powered from the rails, so step one has to come first
        if not progress["power_set"]:
            print("You aim the IR programmer at the rover. Nothing happens.")
            print("Of course, the rails are dead. The rover has no power to listen with.")
            return

        print("You hold the IR programmer over the rover's sensor window.")
        print("Chassis sticker: (40 + 20) / 2 kHz")

        frequency = input("\nCarrier frequency in kHz > ").strip()

        if not frequency.isnumeric():
            print("The programmer only accepts a whole number of kHz.")
            return

        if int(frequency) == CORRECT_FREQUENCY:
            progress["rover_calibrated"] = True
            print(f"\nBeep-boop. The rover locks onto {CORRECT_FREQUENCY} kHz and its LED turns amber.")
            print("It's waiting for a start command.")
        else:
            print(f"\nBEEP! {frequency} kHz rejected, the sensor stays dark.")
            print("Brackets first: work out the sum inside them before you divide.")

    def handleStartRover() -> None:
        """
        Handles starting the rover once both halves of the puzzle are solved.

        This function checks that the rails are powered and the IR link is synced,
        then plays the puzzle animation, marks the room as completed, adds the
        security dongle to the inventory and pays the lab prize into the coin
        balance shown in the status bar.

        Inputs: NONE

        Outputs: NONE
        """

        # Refuse to start and say exactly which step is still missing
        if not progress["power_set"]:
            clearScreen()
            print("You press start. Silence. The rails still have no power.")
            return

        if not progress["rover_calibrated"]:
            clearScreen()
            print("You press start. The rover twitches once and stops.")
            print("It hasn't got a carrier frequency to follow.")
            return

        showActivityAnimation("qte")
        sleep(1)
        clearScreen()

        print("The rover's twin motors buzz to life.")
        print("It tears down the test track, swerves around two cones, and slams")
        print("onto the target pad at the far end. A hatch pops open in its side.")
        print("")

        # Mark the room complete and hand out the rewards
        state["completed"]["classroomd2015"] = True
        state["inventory"].append("security dongle")
        state["coin_balance"] += ROVER_REWARD

        print("Inside the hatch: a small USB 'security dongle' with an Equinox logo")
        print("etched on the casing, and the lab's prize money.")
        print(f"You pocket both. (+{ROVER_REWARD} coins)")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clearScreen()
            handleLook()

        elif command == "?":
            clearScreen()
            handleHelp()

        elif command.startswith("take "):
            clearScreen()
            item = command[5:].strip()
            handleTake(item)

        elif command.startswith("go "):
            clearScreen()
            destination = command[3:].strip()
            result = handleGo(destination)
            if result:
                return result

        elif command == "set power":
            handleSetPower()

        elif command == "calibrate rover":
            handleCalibrateRover()

        elif command == "start rover":
            handleStartRover()

        elif command == "quit":
            clearScreen()
            print("👋 You switch off the bench supply and call it a day. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
