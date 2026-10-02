# -----------------------------------------------------------------------------
# File: loader.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe
# -----------------------------------------------------------------------------


import os
import random
import time
from typing import Literal

from rich.console import (
    Console,
)
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
)


def loader(
    loading_time: float | int = 0.5,
    label: str = "Loading...",
    console: Console | None = None,
    mode: Literal["LOADER", "PROGRESS"] = "LOADER",
    sequence: list | None = None,
    color: str = "green",
) -> None:
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
        mode: Either LOADER or PROGRESS.
        sequence: Sequence of tasks to show.
        color: Color of the loading indicator.

    Returns:
        None
    """

    if console is None:
        console = Console()

    if loading_time > 0:
        if os.getenv("PYCHARM_HOSTED"):
            if mode == "LOADER":
                print(label)
            time.sleep(loading_time)
        else:
            if console is None:
                console = Console()
            if mode == "PROGRESS":
                with Progress(
                    BarColumn(complete_style=color),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    names = sequence or [label]
                    ticks_per_task = random.randint(10, 30)
                    for name in names:
                        console.print(f"[bold]{name}[/]")
                        task = progress.add_task("", total=100)
                        for _ in range(ticks_per_task):
                            progress.update(
                                task,
                                advance=100 / ticks_per_task,
                            )
                            time.sleep(loading_time / (ticks_per_task * len(names)))
                        progress.remove_task(task)
            else:
                with console.status(
                    f"[bold {color}]{label}[/]",
                    spinner="dots",
                ) as status:
                    if sequence:
                        for _ in sequence:
                            status.update(_)
                            time.sleep(loading_time)
                        time.sleep(loading_time)
