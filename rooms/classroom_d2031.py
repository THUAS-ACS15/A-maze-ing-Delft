# -----------------------------------------------------------------------------
# File: classroom_d2031.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Classroom D2.031 (needs the Seating plan): decrypt the professor's message to get the Classroom 2.021 key."""

from rooms.project_room_1 import ask, run_room, say

# Caesar cipher: every letter of the password is moved forward by SHIFT places.
SHIFT = 3
PLAINTEXT = "sesame"


# Turn the plain word into its encrypted form (e.g. sesame -> VHVDPH).
def _encrypt(word: str) -> str:
    return "".join(chr((ord(c) - 97 + SHIFT) % 26 + 97) for c in word).upper()


def _board(state: dict) -> None:
    """The board holds the ENCRYPTED password. It is not the password itself, it must be decrypted."""
    say("[#ffd75f]Scrawled on the board, in the professor's handwriting:[/]")
    say(f'[#ffd75f]    "KEY BOX PASSWORD (ENCRYPTED):  {_encrypt(PLAINTEXT)}"[/]')
    say("[dim]Under it: 'Caesar cipher. Every letter was pushed FORWARD 3 places in the alphabet.'[/]")
    say("[dim]'I switched one monitor on for you. It shows how to decode.'[/]")


def _monitors(state: dict) -> None:
    """One monitor still works and shows the decoder table, so the monitors have a purpose."""
    say("[#5fd7ff]Every screen is dead except one, flickering green. It shows a decoder table:[/]")
    say("[#87ff87]    ENCRYPTED:  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z[/]")
    say("[#87ff87]    DECRYPTED:  X Y Z A B C D E F G H I J K L M N O P Q R S T U V W[/]")
    say("[dim]Example: D on the board is really A. Look up each letter of the board message.[/]")


# Mini game: the player decrypts the board message (shift every letter back by 3). 3 attempts per try.
def decrypt_game(state: dict) -> bool:
    say("[#ffd75f]The key box wants the real password. The board only shows it in code.[/]")
    say("[dim]Read the board and the working monitor first (inspect board, inspect monitors).[/]")
    for attempt in range(3):
        guess = ask("Decrypted password > ").strip().lower()
        if guess == PLAINTEXT:
            say("[bold #87ff87]🔓 Click. The key box opens.[/]")
            say("[#5fd7ff]A tag on the key reads: 'Classroom 2.021. Also fits the Project Room 1 side door.'[/]")
            return True
        say("[#ffaf5f]Nothing happens. Shift every letter BACK by 3 to decrypt it.[/]")
        if attempt == 1:
            say(f"[dim]Hint: D becomes A, so {_encrypt(PLAINTEXT)[0]} becomes {PLAINTEXT[0].upper()}.[/]")
    return False


# Entry point. The door needs the Seating plan (from D2.035); the reward is the Classroom 2.021 key.
def enter_classroom_d2031(state: dict) -> str:
    return run_room(state, {
        "key": "classroomd2031",
        "title": "CLASSROOM D2.031",
        "emoji": "🔌",
        "color": "#5fd7ff",
        "intro": [
            "[#5fd7ff]A dim classroom full of dead monitors. A locked key box is bolted to the wall.[/]",
            "[#af87ff]The seating plan from D2.035 shows this room's seat numbers.[/]",
        ],
        "lock": {"items": ["Seating plan"],
                 "text": "The door is locked. A slot on it matches a seating plan. (use Seating plan on door)",
                 "ok": "The plan matches the slot. The door unlocks."},
        "objects": {"board": _board, "monitors": _monitors, "keybox": ""},
        "game": {"name": "KEY BOX CIPHER", "object": "keybox", "play": decrypt_game},
        "reward": "Classroom 2.021 key",
        "loot_text": "Inside the key box: the Classroom 2.021 key.",
    })
