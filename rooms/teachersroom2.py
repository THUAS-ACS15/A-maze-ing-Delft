# -----------------------------------------------------------------------------
# File: teachersroom2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clearScreen

def enterTeachersRoom2(state):
    clearScreen()
    print("You step into Teachers Room 2.")
    print("A teacher is drawing tables and arrows on a big whiteboard, loks to be a database diagram.")
    print("Papers with rows and columns are taped up everywhere.")

    def handle_look():
        print("\nYou take a look around.")
        print("\nEverything in the rooms appears to be perfectly organized and all of the files and documents sorted and in order,"
              "\njust like a proper database should be")

