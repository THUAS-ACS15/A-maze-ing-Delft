# -----------------------------------------------------------------------------
# File: equinox_society.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from rich.console import Console
from rich.prompt import Prompt
from art import text2art  # type: ignore[import-untyped]
from time import sleep

from utilities.animations import show_activity_animation
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.get_help import get_help
from utilities.print_line import print_line
from utilities.save_gui import display_save_menu

room_commands = [
    (
        "sit down",
        "Sit down at the office chair and check out the computer.",
    )
]

# Format: [question, answer options, correct answer].
quiz_questions: list[tuple[str, dict[str, str], str]] = [
    (
        "How many locations does De Haagse Hogeschool have in total?",
        {"a": "1", "b": "3", "c": "7", "d": "5"},
        "d",
    ),
    (
        "Who teaches the course \"Intercultural Collaboration\"?",
        {"a": "Vineet", "b": "Renee", "c": "Aram", "d": "Sam"},
        "c",
    ),
    (
        "What platform do we use for online course info & assignments?",
        {"a": "Brightspace", "b": "OSIRIS", "c": "Microsoft Teams", "d": "Google"},
        "a",
    ),
    (
        "Which language is primarily used in this Q1 Project?",
        {"a": "HTML", "b": "Python", "c": "CSS", "d": "SQL"},
        "b",
    ),
    (
        "What is the capital city of the Netherlands?",
        {"a": "Delft", "b": "Rotterdam", "c": "The Hague", "d": "Amsterdam"},
        "d",
    ),
    (
        "Who's the current monarch of the Netherlands?",
        {"a": "Beatrix", "b": "Willem-Alexander", "c": "William Frederick", "d": "Wilhelmina"},
        "b",
    ),
]

def enter_equinox_student_society(state: dict) -> str:
    """Starter function for the Equinox Student Society room."""

    clear_screen()
    print("📚 You scan your student ID on the doorknob and enter the Equinox Student Society room.")
    print("The room is well-lit and organized, with a few tables and chairs arranged neatly.")
    print("A computer is set up on an office table, and a small shelf holds some books and board games.")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        box stacking puzzle. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """

        print("  You look around and can only describe a really organized room. The center has a")
        print(" table with 3 chairs, and an opened board game box on it.")
        print("  The left corner has a usual office desk with a computer on it. The office chair")
        print(" looks very comfortable, like newly bought.")
        print(" The right corner has a small shelf with some books and a few board game boxes in it.")
        if not state["completed"]["equinoxstudentsociety"]:
            print("\n You take a close look at the table, and notice")
            print("that there is a small statue of a dragon on it. It seems to be guarding some treasure!")
            if not state["equinox_coins_claimed"]:
                print("  Next to it, you find some coins. Looks like it was hoarding some treasure.")
                print(" Thankfully it's just a statue, so you pick them up. (+10 coins)")
                state["coin_balance"] += 10
                state["equinox_coins_claimed"] = True
            else:
                print(" You've already collected the coins that were next to it. Now the dragon is broke.")
        else:
            print(" You've already finished the quiz and claimed your reward, so there's nothing else to do here.")
        print("- Possible exits: lobby")
        print(
            "- Your current inventory:",
            state["inventory"],
        )

    def handle_go(destination: str) -> str | None:
        """
        Handles movement out of the room.

        This function checks if the player can move to the given destination from this room.
        If the destination is valid, it returns the destination string. Otherwise, it
        prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.

        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
        valid_destinations = ["lobby", "back"]

        if destination in valid_destinations:
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def handle_quiz_start() -> None:
        """
        Boots the computer at the desk, and prompts for a start command to start the quiz.

        This function handles the quiz interaction with the player.
        It displays the quiz questions, collects answers, and calculates the score. 
        If the player completes the quiz, they receive a certificate and coins.

        Inputs: NONE

        Outputs: NONE
        """

        if state["completed"]["equinoxstudentsociety"]:
            print("The computer has shut down after you finished the quiz.")
            print("You can't seem to be able to get it to boot up again, so you decide to leave it alone.")
            return

        clear_screen("use \"start\" to start or \"quit\" to stop")
        console = Console(legacy_windows=False)
        clear_screen("use \"start\" to start or \"quit\" to stop")
        print_line(text2art("NIX OS", font="univers", chr_ignore=True), delay=0.002)
        sleep(1.0)
        print_line(text="[bold green]NIXOS // eqnx-pc[/]")
        print_line("[dim]NixOS 26.05 (Linux 6.12.1)[/]")
        sleep(1.0)
        print_line('\nType "start" to begin or "quit" to return to the room.', console=console)

        command = Prompt.ask(
            "[bold green]student@hhs:~$[/]",
            choices = ["start", "quit", "?"],
            show_choices = False,
            console = console,
        )

        if command == "quit":
            clear_screen()
            print("You step away from the computer.")
            return

        clear_screen("use \"start\" to start or \"quit\" to stop")
        show_activity_animation("quiz")
        score = 0
        for number, (question, options, correct_answer) in enumerate(quiz_questions, start=1):
            clear_screen()
            console.print(f"[bold green]Question {number}/{len(quiz_questions)}[/]")
            console.print(question)
            for option, answer in options.items():
                console.print(f"  [bold]{option})[/] {answer}")

            answer = Prompt.ask(
                "[bold green]Answer[/]",
                choices = ["a", "b", "c", "d"],
                show_choices = False,
                console = console,
            )
            if answer == correct_answer:
                score += 1

        clear_screen()
        if score <= 3:
            console.print(f"[bold red]Quiz complete. {score}/{len(quiz_questions)} correct.[/]")
            console.print("[bold red]You did not answer enough questions correctly to pass the quiz.[/]")
            console.print("[bold red]Please try again.[/]")
        else:
            console.print(f"[bold green]Quiz complete. {score}/{len(quiz_questions)} correct.[/]")
            if score == len(quiz_questions):
                console.print("[bold green]Congratulations! You answered all questions correctly![/]")
            print("For your efforts, you receive a certificate of completion!")
            state["completed"]["equinoxstudentsociety"] = True
            state["inventory"].append("Quiz certificate")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            get_help(room_commands)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "sit down":
            handle_quiz_start()

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print("👋 You decide to try your hand at the Dungeons and Dragons game, and lose track of time. Game over.")
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
