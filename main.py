import io
import sys
import src.config  # noqa: F401  (loads .env)

from typing import cast

cast(io.TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    from src.engine import run
    from src.room import render
    render()
    run()
