# -----------------------------------------------------------------------------
# File: main_menu.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Joao
# -----------------------------------------------------------------------------
from utilities.clear_screen import clear_screen
from rich.console import Console
from rich.align import Align


# ASCII Font is Blunder
GAME_TITLE_ART: str = """
██▀██     ██▀██▀██ ██▀██ ██▀██ ██▀██     ▀██▀ ███▄██ ██▀██       ██▀█▄ ██▀██ ██    ██▀██ ▀██▀
██▄██ ███ ██ ██ ██ ██▄██ ▄▄▄██ ██▄   ███  ██  ██ ▀██ ██ ▀▀       ██ ██ ██▄   ██    ██▄    ██ 
█▓░█▓     █▓░█▓░█▓ █▓░█▓ ▓█ ▄▄ █▓░▄▄      █▓░ █▓░ █▓ █▓░██▀      █▓░█▓ █▓░▄▄ █▓░▄▄ █▓░    █▓░
▀▀ ▀▀     ▀▀    ▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀▀     ▀▀▀▀ ▀▀  ▀▀ ▀▀▀▀▀       ▀▀▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀▀     ▀▀ """

def display_main_menu() -> None:
    clear_screen()
    console = Console()
    console.print(Align.center(GAME_TITLE_ART, vertical = "middle"))
