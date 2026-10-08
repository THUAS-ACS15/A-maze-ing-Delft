# -----------------------------------------------------------------------------
# File: project_room_1.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Project Room 1: Professor Vance's locker room.

HOW THIS FILE IS ORGANISED
1. PART 1 (top): the Project Room 1 code. It is plain and self-contained: one function,
   enter_project_room1(), with its own command loop and every dialogue line written as a print().
2. PART 2 (bottom): TEMPORARY compatibility code. front_desk.py, classroom_d2015.py, classroom_d2031.py and
   classroom_d2035.py still import say / ask / run_room from this file. Part 2 keeps them working so the
   game does not crash. Once those four files are replaced with the standalone versions, delete Part 2
   (everything below the "PART 2" banner) and the imports it needs (os, re, rich).
"""

import os
import re
import sys
import time
from typing import TypedDict

from rich.console import Console
from rich.errors import MarkupError
from rich.text import Text

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# =============================================================================
# PART 1: PROJECT ROOM 1
# =============================================================================

class Locker(TypedDict):
    """One locker: its BODMAS code (None = opens with the brass key), the coins inside and the item inside."""

    code: int | None
    coins: int
    item: str | None


LOCKERS: dict[str, Locker] = {
    "1": {"code": 182, "coins": 50, "item": "Sensory Module"},
    "2": {"code": None, "coins": 0, "item": "USB cable"},
    "3": {"code": 24, "coins": 20, "item": "Teachers Room 4 Keycard"},
    "4": {"code": 30, "coins": 30, "item": None},
    "5": {"code": 46, "coins": 20, "item": None},
}
# Items that open the door: the key from Classroom D2.031 or a staff keycard.
ENTRY_ITEMS = ["Classroom 2.021 key", "Level-1 Staff Keycard", "Level 1 Staff Keycard", "Teacher Access Keycard"]


def enter_project_room1(state):
    """Project Room 1: Professor Vance's locker room (Sensory Module, USB cable, Teachers Room 4 keycard)."""
    key = "projectroom1"
    state["completed"].setdefault(key, False)
    loot = state.setdefault("room_loot", {}).setdefault(key, ["brass key"])  # items lying around the room
    unlocked = state.setdefault("room_unlocked", {})  # which locked doors are already open
    progress = state.setdefault("projectroom1_progress", {"opened": []})  # lockers that are already open

    if state["completed"][key]:
        clear_screen()
        print("You have already completed this room. There is nothing else to do here.")
        time.sleep(2)
        return "lobby"

    clear_screen()
    print("You stand in front of Project Room 1.")
    if not unlocked.get(key):
        print("INVITATION ONLY. You need a key or staff keycard. (Try: use <item> on door)")
    else:
        print("A project room. Professor Vance stands at the front, capping a whiteboard marker.")
        print("Five lockers line the back wall.")

    def handle_look():
        print("You take a look around.")
        if not unlocked.get(key):
            print("The door is shut.")
        else:
            print("Things you can inspect: whiteboard, desks, pile, vance, lockers")
            if loot:
                print("On the floor:", ", ".join(loot))
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("Available commands:")
        print("- look around         : Describe the room.")
        print("- inspect <object>    : Look closer (try the lockers).")
        print("- take <item>         : Pick up an item.")
        print("- use <item> on door  : Unlock the door with an item.")
        print("- go lobby / back     : Leave the room.")
        print("- status / save       : Show your status / open the save menu.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def play_lockers():
        # Type a locker number and its BODMAS code. Locker 2 needs the brass key instead of a code.
        while len(progress["opened"]) < len(LOCKERS):
            print("\nBack wall:")
            for number in LOCKERS:
                print(f"  Locker {number}: " + ("open" if number in progress["opened"] else "shut"))
            choice = input("Which locker (1-5)? ('back' to step away) > ").strip().lower()
            if choice == "back":
                print("Vance calls after you: \"The lockers will still be here!\"")
                return False
            if choice not in LOCKERS:
                print("There are only five lockers, numbered 1 to 5.")
                continue
            if choice in progress["opened"]:
                print("That one is already open and empty.")
                continue
            locker = LOCKERS[choice]
            if locker["code"] is None:
                if "brass key" not in state["inventory"]:
                    print("Locker 2 has an old brass padlock. The key must be in the pile in the corner.")
                    continue
                print("You try the brass key. Click, it turns.")
            else:
                code = input(f"Code for locker {choice} > ").strip()
                if not code.isdigit() or int(code) != locker["code"]:
                    print("BZZT. The keypad resets. BODMAS: do the multiplication BEFORE adding or subtracting.")
                    continue
                print(f"Click. Locker {choice} swings open.")
            progress["opened"].append(choice)
            if locker["coins"]:
                state["coin_balance"] += locker["coins"]
                print(f"Cash inside. (+{locker['coins']} coins)")
            if locker["item"]:
                state["inventory"].append(locker["item"])
                print(f"You find: {locker['item']}. (Added to your inventory)")
        print("All five lockers are open. Vance applauds, once. \"Now get out of my room.\"")
        return True

    def handle_inspect(obj):
        if not unlocked.get(key):
            print("The door is shut. Try 'use <item> on door'.")
        elif obj == "whiteboard":
            print("You step up to the whiteboard. Vance's handwriting is terrible.")
            print('    "LOCKER 1:  2 + 6 * 30"')
            print('    "LOCKER 3:  (2 + 6) * 3"')
            print("Vance has added a reminder: BODMAS. Brackets first, then multiply/divide, then add/subtract.")
            print("(Two more codes are written somewhere else in the room.)")
        elif obj == "desks":
            print("Between the rows of wooden desks, something is carved into desk #3:")
            print('    "LOCKER 4:  50 - 5 * 4"')
        elif obj == "pile":
            print("A pile of broken desks and chairs. A sticker peels off a snapped chair:")
            print('    "LOCKER 5:  2 ** 4 + 3 * 10"')
            print("Something shiny is half buried in the pile (try 'look' and 'take').")
        elif obj == "vance":
            print("Vance: \"Five lockers, five combinations, every number is somewhere in this room.")
            print("The USB cable and the keycard for the old Linux room are in there. Earn them.\"")
        elif obj == "lockers":
            if play_lockers():
                state["completed"][key] = True
            else:
                print("No worries, inspect the lockers again whenever you like to continue.")
        else:
            print(f"There is no '{obj}' here.")

    def handle_take(item):
        for thing in loot:
            if item and item in thing.lower():
                loot.remove(thing)
                state["inventory"].append(thing)
                print(f"You took the {thing}.")
                return
        print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["lobby", "back"]:
            print("You leave Vance to his lockers and step back into the lobby.")
            return "lobby"
        print(f"You can't go to '{destination}' from here.")
        return None

    def handle_use(item, target):
        owned = next((i for i in state["inventory"] if i.lower() == item), None)
        if owned is None:
            print(f"You don't have '{item}'.")
        elif target == "door" and not unlocked.get(key) and owned in ENTRY_ITEMS:
            unlocked[key] = True
            print("Beep! The door clicks open.")
        else:
            print("Nothing happens.")

    while True:
        command = input("\n> ").lower().strip()

        if command in ["look around", "look", "ls"]:
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("inspect "):
            clear_screen()
            handle_inspect(command[8:].strip())

        elif command.startswith("take "):
            clear_screen()
            handle_take(command[5:].strip())

        elif command.startswith("use ") and " on " in command:
            clear_screen()
            item, target = command[4:].split(" on ", 1)
            handle_use(item.strip(), target.strip())

        elif command.startswith("go "):
            clear_screen()
            result = handle_go(command[3:].strip())
            if result:
                return result

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print("You leave Project Room 1 and exit the maze.")
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")


# =============================================================================
# PART 2: TEMPORARY COMPATIBILITY CODE (delete once the other four rooms are standalone)
# =============================================================================
# -----------------------------------------------------------------------------
# Shared helpers + room engine (used by Front Desk, D2.015, D2.031, D2.035 and
# this room). They live here so that no extra utility files are needed.
# -----------------------------------------------------------------------------
# Message shown when the player returns to a room they already finished.
ALREADY_DONE = "You have already completed this room. There is nothing else to do here."

# Colour setup: the Rich console prints coloured text (see say() below).
if os.name == "nt":
    os.system("")  # switches on ANSI colours in the Windows terminal
# force_terminal keeps the colours on even in IDE consoles that Rich would treat as plain text
console = Console(highlight=False, force_terminal=not os.getenv("NO_COLOR") or None)
# Colours used for banners and the loading bar.
PALETTE = ["#ff5f87", "#ffaf5f", "#ffd75f", "#87ff87", "#5fd7ff", "#af87ff"]


def _sleep(seconds: float) -> None:
    """Sleep, unless AMAZE_FAST is set (used for automated tests)."""
    if not os.getenv("AMAZE_FAST"):
        time.sleep(seconds)


def rainbow(text: str) -> Text:
    """Return text with every character in a different palette colour."""
    out = Text()
    for i, ch in enumerate(text):
        out.append(ch, style=f"bold {PALETTE[i % len(PALETTE)]}")
    return out


def say(markup: str) -> None:
    """Print a line of rich markup, e.g. say('[cyan]hello[/]')."""
    try:
        console.print(markup)
    except MarkupError:  # a stray [/] must never crash the game
        console.print(Text(re.sub(r"\[/?[^\]]*\]", "", markup)))


def ask(prompt: str) -> str:
    """input() with a coloured prompt (bright cyan)."""
    return input(f"\033[1;96m{prompt}\033[0m")


def typewrite(markup: str, delay: float = 0.012) -> None:
    """Print a line one character at a time (no delay when AMAZE_FAST is set)."""
    text = Text.from_markup(markup)
    if os.getenv("AMAZE_FAST"):
        console.print(text)
        return
    for i in range(len(text)):
        console.print(text[i], end="")
        time.sleep(delay)
    console.print()


def banner(title: str, emoji: str = "") -> None:
    """Rainbow room title with a short sparkle animation."""
    line = f"{emoji}  {title}  {emoji}".strip()
    for shift in range(3):
        rotated = line[shift:] + line[:shift]
        console.print(rainbow(rotated), end="\r")
        _sleep(0.08)
    console.print(rainbow(line))
    console.print("[dim]" + "~" * (len(line) + 4) + "[/]")


def robot_blink(message: str = "A.I.G.I.S. approves!") -> None:
    """Tiny animated robot face shown when a quest is completed."""
    frames = ["(o_o)", "(-_-)", "(o_o)", "(^_^)"]
    for i, f in enumerate(frames):
        console.print(f"  [bold {PALETTE[i % 6]}]{f}[/]", end="\r")
        _sleep(0.15)
    console.print(f"  [bold #87ff87](^_^)[/] [bold #ffd75f]{message}[/]")


def loading(label: str, steps: int = 12) -> None:
    """Coloured progress bar animation."""
    for i in range(steps + 1):
        bar = "█" * i + "░" * (steps - i)
        console.print(f"  [{PALETTE[i % 6]}]{bar}[/] [dim]{label}[/]", end="\r")
        _sleep(0.05)
    console.print()


# Small helper: True if the player carries at least one of the named items.
def has_any(state: dict, names) -> bool:
    return any(n in state["inventory"] for n in names)


# HOW IT RUNS: every room (Front Desk, D2.015, D2.031, D2.035) describes itself with a cfg dict and
# this one function plays it: a loop reads commands (look / inspect / take / use / go) until the player leaves.
# The saved game state is the dict "state": inventory, coin_balance, completed (per room), room_loot, room_unlocked.
def run_room(state: dict, cfg: dict) -> str:
    """Run one room. cfg keys: key, title, emoji, color, intro, objects,
    game (name/object/play), reward, loot_text, lock (optional), on_leave."""
    # Room id, e.g. "classroomd2035". It is the key used in state["completed"].
    key = cfg["key"]
    done = state["completed"]
    done.setdefault(key, False)
    # Loot lying in each room is stored in state, so taken items never reappear.
    all_loot = state.setdefault("room_loot", {})
    if key not in all_loot:
        all_loot[key] = list(cfg.get("start_loot", []))  # loose items lying around
    loot = all_loot[key]
    # Rewards (one or more items) appear on the floor only after the puzzle is solved.
    rewards = cfg.get("reward") or []
    if isinstance(rewards, str):
        rewards = [rewards]
    pending = lambda: [i for i in loot if i in rewards]  # noqa: E731
    # Doors: a room with a "lock" stays shut until the player uses the right item on the door.
    state.setdefault("room_unlocked", {})
    unlocked = lambda: (not cfg.get("lock")) or state["room_unlocked"].get(key, False)  # noqa: E731
    color = cfg.get("color", "cyan")

    # Clear the screen and draw the title, story text and (if shut) the locked-door notice.
    def show_room() -> None:
        clear_screen()
        banner(cfg["title"], cfg.get("emoji", ""))
        for line in cfg["intro"]:
            typewrite(line)
        if not unlocked():
            say(f"[bold red]🔒 {cfg['lock']['text']}[/]")

    # "look" / "ls": list the objects, loot on the floor, exits and inventory.
    def handle_look() -> None:
        show_room()
        if unlocked():
            say(f"\n[bold {color}]You can inspect:[/] " + ", ".join(f"[yellow]{o}[/]" for o in cfg["objects"]))
            if loot:
                say("[bold green]On the floor:[/] " + ", ".join(f"[green]{i}[/]" for i in loot))
            if done[key]:
                say("[dim]✔ Quest complete in this room.[/]")
        say("[bold]Exits:[/] [magenta]lobby[/]")
        say(f"[bold]Inventory:[/] {state['inventory']}")

    # "?" / "help": print the command list.
    def handle_help() -> None:
        say(f"[bold {color}]Commands[/]")
        for c, d in [
            ("look / ls", "describe the room, objects and exits"),
            ("inspect <object>", "look closer (the game object starts the quest)"),
            ("take <item>", "pick up an item"),
            ("use <item> on <target>", "e.g. use Student ID card on door"),
            ("go lobby", "leave the room"),
            ("status / save / quit", "game menus"),
        ]:
            say(f"  [yellow]{c:<24}[/] {d}")

    # "inspect <object>": the room's game object starts the puzzle; other objects show a clue.
    def handle_inspect(obj: str) -> None:
        if not unlocked():
            say("[red]The door is shut. Try 'use <item> on door'.[/]")
            return
        game = cfg["game"]
        if obj == game["object"]:
            if done[key]:
                say(f"[bold green]✔ {ALREADY_DONE}[/]")
                return
            clear_screen()
            banner(game["name"], "🎮")
            # Run the mini game. It returns True when solved: mark the room completed and drop the rewards.
            if game["play"](state):
                done[key] = True
                loot.extend(rewards)
                robot_blink()
                if rewards:
                    say(f"[bold green]🎁 {cfg['loot_text']}[/] Use [yellow]take <item>[/] to pick it up.")
            else:
                say("[yellow]No worries, inspect it again whenever you like to retry.[/]")
        elif obj in cfg["objects"]:
            text = cfg["objects"][obj]
            if callable(text):
                text(state)
            else:
                say(text)
        else:
            say(f"[red]There is no '{obj}' here.[/]")

    # "take <item>": move an item from the floor into the inventory (partial names work).
    def handle_take(item: str) -> None:
        for have in loot:
            if item and item in have.lower():
                loot.remove(have)
                state["inventory"].append(have)
                say(f"[bold green]✔ You took the {have}.[/]")
                coins = cfg.get("item_coins", {}).get(have)
                paid = state.setdefault("coins_paid", [])
                if coins and have not in paid:  # coins hidden inside an item, paid once
                    paid.append(have)
                    state["coin_balance"] += coins
                    say(f"[bold yellow]Something was hidden inside it. Coins! (+{coins} coins)[/]")
                return
        say(f"[red]There is no '{item}' to take.[/]")

    # "use <item> on door": unlocks the room when the item is the right key.
    def handle_use(item: str, target: str) -> None:
        owned = next((i for i in state["inventory"] if i.lower() == item), None)
        if owned is None:
            say(f"[red]You don't have '{item}'.[/]")
            return
        lock = cfg.get("lock")
        if lock and not unlocked() and target == "door" and owned in lock["items"]:
            state["room_unlocked"][key] = True
            say(f"[bold green]🔓 Beep! {lock['ok']}[/]")
            show_room()
            return
        say("[dim]Nothing happens.[/]")

    # Already completed? Skip the puzzle (state["completed"][key] is the saved flag).
    # If the reward is still lying on the floor the player may come in to take it.
    # Already completed and nothing left to collect: skip the room with the "already completed" message.
    if done[key] and not pending() and not cfg.get("reenter"):
        clear_screen()
        say(f"[bold green]✔ {ALREADY_DONE}[/]")
        _sleep(2.0)
        state["previous_room"] = key
        return "lobby"

    show_room()
    while True:
        # Main command loop: read one command and call the matching handler.
        cmd = ask("\n> ").strip().lower()
        if cmd in ("look", "ls", "look around"):
            handle_look()
        elif cmd in ("?", "help"):
            handle_help()
        elif cmd.startswith("inspect "):
            handle_inspect(cmd[8:].strip())
        elif cmd.startswith("take "):
            handle_take(cmd[5:].strip())
        elif cmd.startswith("use ") and " on " in cmd:
            item, target = cmd[4:].split(" on ", 1)
            handle_use(item.strip(), target.strip())
        elif cmd in ("go lobby", "go back", "back"):
            state["previous_room"] = key
            return "lobby"
        elif cmd.startswith("go "):
            say("[red]The only exit is the lobby.[/]")
        elif cmd in ("status", "check status"):
            clear_screen()
            check_status(state, pause=True)
        elif cmd in ("pause", "save"):
            display_save_menu(state)
        elif cmd == "quit":
            clear_screen()
            say("[bold]👋 You leave the school and the adventure comes to an end. Game over.[/]")
            sys.exit()
        else:
            say("[red]❓ Unknown command. Type '?' for help.[/]")