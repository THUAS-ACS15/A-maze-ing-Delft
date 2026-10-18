import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    from src.engine_functional import run
    from src.room_functional import render
    render()
    run()
