"""Entry point for A-maze-ing Delft, a terminal text-adventure.

Importing ``config`` first is required: it loads ``.env`` and runs ``db.init()`` and ``state.init()`` so the
database schema and the in-memory game state exist before the engine starts. When executed as a script the
current room is rendered once and the main loop in :func:`src.engine.run` takes over until the player quits.
"""

import io
import sys
import config  # noqa: F401  (loads .env)

from typing import cast

from src.engine import run
from src.room import render

cast(io.TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    render()
    run()
