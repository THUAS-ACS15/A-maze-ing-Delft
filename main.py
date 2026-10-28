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
