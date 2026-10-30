# -----------------------------------------------------------------------------
# File: equinox_society.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

"""Equinox Student Society: optional quiz room awarding a quiz certificate."""

import sys

from rich.console import Console
from rich.prompt import Prompt
from art import text2art  # type: ignore[import-untyped]
from time import sleep

from utilities.animations import show_activity_animation
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.centralized_commands import display_help
from utilities.inventory_viewer import display_inventory
from utilities.print_helpers import print_current_objective, print_line
from utilities.print_helpers import print_dialogue
from utilities.save_gui import display_save_menu
from utilities.game_map import display_map

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

valid_destinations = ["studentwing"]
room_dialogue_bank = story_dialogue_bank["rooms"]["equinoxstudentsociety"]

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

    state["previous_room"] = "equinoxstudentsociety"

    clear_screen()
    state["visited"]["equinoxstudentsociety"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])
    print_dialogue(room_dialogue_bank["enter_computer_desc"])

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        box stacking puzzle. It also shows the possible exits and the
        player's current inventory.
        """

        print_dialogue(look_around_dialogue_bank["equinoxstudentsociety"])
        if not state["completed"]["equinoxstudentsociety"]:
            print("\n You take a close look at the table, and notice")
            print("that there is a small statue of a dragon on it. It seems to be guarding some treasure!")
            print("Seems like it's just a decoration, but you wonder if it has any significance to the game.")
        else:
            print(" You've already finished the quiz and claimed your reward, so there's nothing else to do here.")
        print(f"- Possible exits: {', '.join(valid_destinations)}")
        print()
        print_current_objective(state)

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def handle_quiz_start() -> None:
        """Boots the computer at the desk, and prompts for a start command to start the quiz.

        This function handles the quiz interaction with the player.
        It displays the quiz questions, collects answers, and calculates the score.
        If the player completes the quiz, they receive a certificate.
        """

        if state["completed"]["equinoxstudentsociety"]:
            print_dialogue(room_dialogue_bank["quiz_shutdown"])
            print_dialogue(room_dialogue_bank["quiz_no_boot"])
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
            print_dialogue(room_dialogue_bank["step_away"])
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
            print_dialogue(room_dialogue_bank["certificate"])
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
            display_help(room_commands)

        elif command in ["g", "go", "goto", "move"] or command.startswith("go "):
            result = display_selection_menu("Choose room to go to:", valid_destinations)
            if result:
                return result

        elif command == "sit down":
            handle_quiz_start()

        elif command == "map":
            display_map(state)

        elif command in ["inv", "inventory"]:
            clear_screen()
            display_inventory(state["inventory"])

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
