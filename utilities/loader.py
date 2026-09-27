# -----------------------------------------------------------------------------
# File: loader.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe
# -----------------------------------------------------------------------------


import os
import time
from rich.console import Console

def loader (loading_time: float | int = 0.5, label: str = "Loading...", console: Console = Console()) -> None:
    """
       Display a short loading indicator for a given amount of time.

       In PyCharm, this prints the label directly and pauses for the specified
       duration. In other terminal environments, it uses Rich's status spinner
       while waiting.

       Args:
           loading_time: Number of seconds to display the loader. Must be greater
               than 0 to show anything.
           label: Text shown while loading.
           console: Optional Rich Console instance. If not provided, a new Console
               is created.

       Returns:
           None
       """
    if loading_time > 0:
        if os.getenv("PYCHARM_HOSTED"):
            print(label)
            time.sleep(loading_time)
        else:
            with console.status(f"[bold cyan]{label}[/]", spinner="dots"):
                time.sleep(loading_time)