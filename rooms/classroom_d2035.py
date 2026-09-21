# -----------------------------------------------------------------------------
# File: classroom_d2035.py
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

# Loose items left behind on the front row of desks.
desk_items = ["leather bookmark", "quill pen"]

# The seven lines of the acrostic. The first letter of each line spells the
# answer, but the letters are NOT highlighted, otherwise there is no puzzle.
acrostic_lines = [
    "Entwined in silence, old secrets reside,",
    "Quietly buried where shadows divide.",
    "Under cold stone, where lost scholars speak,",
    "Insight remains for the daring who seek.",
    "Night brings the hour of balance and sight,",
    "Over the halls where day equals night.",
    "X marks the society hidden from light."
]

# The word spelled out by the first letters above.
ACROSTIC_ANSWER = "equinox"

# Reward for cracking the cipher.
CIPHER_REWARD = 30

# How many wrong guesses before the lecturer starts helping out.
HINT_AFTER_GUESSES = 2


def enterClassroomD2035(state: dict) -> str:
    """Starter function for Classroom D2.035."""

    clearScreen()
    state["visited"]["classroomd2035"] = True
    print("📚 You slip into Classroom D2.035, halfway through an English Literature lecture.")
    print("Tiered wooden seating climbs towards the back. Nobody looks up.")
    print("At the front, a lecturer is glaring at a poem chalked across the board")
    print("in handwriting that is clearly not hers.")
    print("Maybe you should read it.")

    # Progress is stored in the state dict so it survives leaving the room.
    if "d2035_progress" not in state:
        state["d2035_progress"] = {
            "wrong_guesses": 0,
            "talked_to_lecturer": False
        }

    progress = state["d2035_progress"]

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printChalkboard() -> None:
        """
        Helper function to print the acrostic poem on the chalkboard.

        This function draws the poem inside a frame and adds a prompt telling
        the player what they are looking for. Once the puzzle has been solved
        it also confirms the answer, so a returning player is not stuck.

        Inputs: NONE

        Outputs: NONE
        """

        print("+-------------------------------------------------------------+")
        print("|                    THE FORBIDDEN UNION                      |")
        print("|                                                             |")

        # Print each line of the poem padded out to the width of the frame
        for line in acrostic_lines:
            print(f"|  {line:<59}|")

        print("|                                                             |")
        print("|  - scrawled below, in a different hand:                     |")
        print("|      \"Read down, not across. Seven letters. Be there.\"      |")
        print("+-------------------------------------------------------------+")

        if state["completed"]["classroomd2035"]:
            print(f"You have already worked this one out: {ACROSTIC_ANSWER.upper()}.")
        else:
            print("Type 'solve' when you think you have the word.")

    def cipherCheck(guess: str) -> bool:
        """
        Checks whether the player's guess matches the acrostic answer.

        The guess is stripped and lowercased first so that spacing and capital
        letters do not matter.

        Inputs:
            - guess (str): The word the player typed in.

        Outputs:
            - bool: True if the guess is correct, False otherwise.
        """

        if guess.strip().lower() == ACROSTIC_ANSWER:
            return True
        else:
            return False

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.

        This function describes the lecture hall, points the player at the
        chalkboard and the lecturer, and lists any items still on the desks.
        It also shows the exits and the player's inventory.

        Inputs: NONE

        Outputs: NONE
        """

        if not state["completed"]["classroomd2035"]:
            print("You take a look around the lecture hall.")
            print("Front: a chalkboard with a seven line poem on it ('read board').")
            print("Podium: the lecturer, arms folded, clearly unimpressed ('talk to lecturer').")
            print("Middle: rows of desks with open Shakespeare and cryptography notes.")
        else:
            print("The chalkboard has been wiped. The lecturer gives you a small nod.")
            print("Whatever the Equinox Society is, she wants nothing more to do with it.")

        if desk_items:
            print("Left on the front desk:", ", ".join(desk_items))
        else:
            print("The desks have been cleared.")

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
        print("- look around         : Examine the lecture hall.")
        print("- read board          : Read the poem chalked on the board.")
        print("- talk to lecturer    : Ask the lecturer about the poem.")
        if not state["completed"]["classroomd2035"]:
            print("- solve               : Submit the word hidden in the poem.")
        print("- take <item>         : Pick up something from the desks.")
        print("- go lobby / back     : Leave the hall and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handleTake(item: str) -> None:
        """
        Handles picking up an item from the lecture desks.

        This function checks whether the named item is still on the desks. If it
        is, the item is moved into the player's inventory.

        Inputs:
            - item (str): The name of the item the player wants to take.

        Outputs: NONE
        """

        if item in desk_items:
            desk_items.remove(item)
            state["inventory"].append(item)
            print(f"You quietly take the {item}.")
        else:
            print(f"❌ There's no '{item}' on the desks.")

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
            print("You duck out of the lecture and back into the Lobby.")
            state["previous_room"] = "classroomd2035"
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handleTalk() -> None:
        """
        Handles talking to the lecturer at the podium.

        Before the puzzle is solved the lecturer explains where the poem came
        from, and drops a stronger hint if the player has already guessed wrong
        a couple of times. Afterwards she warns them about the society.

        Inputs: NONE

        Outputs: NONE
        """

        if state["completed"]["classroomd2035"]:
            print("Lecturer: \"Splendid deduction earlier. Now do me a favour.\"")
            print("\"Whoever is running that society, don't let them know you can read.\"")
            return

        progress["talked_to_lecturer"] = True
        print("Lecturer: \"It was on my board when I unlocked this morning.\"")
        print("\"Some student from the East Wing, I assume. It's an acrostic, obviously.\"")

        # Only give the real hint once the player has struggled a bit
        if progress["wrong_guesses"] >= HINT_AFTER_GUESSES:
            print("")
            print("She sighs and taps the board with her chalk.")
            print("\"The first letter of every line. Read them downwards, top to bottom.\"")
            print("\"Seven lines, seven letters. The night where day and dark are equal.\"")
        else:
            print("\"Work it out yourself. That's rather the point of literature.\"")

    def handleSolve() -> None:
        """
        Handles submitting an answer to the acrostic.

        This function asks the player for the hidden word, checks it, and on a
        correct answer marks the room as completed, adds the cipher note to the
        inventory and pays the reward into the coin balance in the status bar.
        Wrong answers are counted so the lecturer can offer a hint later.

        Inputs: NONE

        Outputs: NONE
        """

        clearScreen()

        if state["completed"]["classroomd2035"]:
            print("You've already cracked this one.")
            return

        guess = input("The word hidden in the poem > ").strip().lower()

        if cipherCheck(guess):
            showActivityAnimation("quiz")
            sleep(1)
            clearScreen()

            state["completed"]["classroomd2035"] = True
            state["inventory"].append("equinox cipher note")
            state["coin_balance"] += CIPHER_REWARD

            print(f"You say it out loud: \"{ACROSTIC_ANSWER.upper()}.\"")
            print("The lecture hall goes very quiet. A few students turn around.")
            print("")
            print("The lecturer pulls a folded note out of her jacket.")
            print("\"This was pinned under the poem. I didn't want it on my board.\"")
            print("It's an invitation, in the same handwriting. A date. A room number.")
            print("")
            print(f"She also presses the department's puzzle prize into your hand. (+{CIPHER_REWARD} coins)")
        else:
            # Count the miss so handleTalk() knows when to offer the real hint
            progress["wrong_guesses"] += 1
            print(f"\"{guess.upper()}\"? The lecturer doesn't even look up.")

            if progress["wrong_guesses"] >= HINT_AFTER_GUESSES:
                print("\"Go on then, ask me. I can see you're stuck.\"")
            else:
                print("Look at how each line begins, not what it says.")

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

        elif command in ["read board", "look at board", "board"]:
            clearScreen()
            printChalkboard()

        elif command in ["talk to lecturer", "talk to professor", "lecturer"]:
            clearScreen()
            handleTalk()

        elif command in ["solve", "answer"]:
            handleSolve()

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

        elif command == "quit":
            clearScreen()
            print("👋 You leave the lecture hall and the poem behind. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
