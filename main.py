import io
import sys
import config  # noqa: F401  (loads .env)
from db import init

from typing import cast

cast(io.TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    from src.engine import run
    from src.room import render
    init()
    render()
    run()
