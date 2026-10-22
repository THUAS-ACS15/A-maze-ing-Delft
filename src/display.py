from subprocess import run

from .utils.colors import BOLD, BRIGHT_MAGENTA, BRIGHT_YELLOW, DIM


def colorize(text: str, color_code: str) -> str:
    from .state import state
    return f"{color_code}{text}\033[0m" if state["enable_colors"] else text

def out(text: str = "") -> None:
    import builtins

    builtins.print(safe(text))

def draw_line(char: str = "-") -> None:
    from .state import state

    out(colorize(char * state["terminal_width"], "\033[2m"))

def safe(text: str) -> str:
    table = str.maketrans({"─": "-", "═": "=", "•": "*", "→": "->", "←": "<-"})
    text = text.translate(table)
    try:
        text.encode("cp1252")
        return text
    except UnicodeEncodeError:
        return text.encode("cp1252", errors="replace").decode("cp1252")

def clear() -> None:
    """Clear the terminal screen (Windows/posix/PyCharm-safe)."""
    try:
        from rich.console import Console

        Console().clear()
    except ModuleNotFoundError:
        import os

        if os.getenv("PYCHARM_HOSTED"):
            import builtins

            builtins.print("\n" * 50)
        else:
            run(["cls" if os.name == "nt" else "clear"], shell=True)

def header() -> None:
    from .state import state

    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    draw_line("═")

    out(
        colorize(f"[{state['game_state']['phase']}]", BRIGHT_MAGENTA)
    )
    out(
        colorize(f"LOCATION: {room_data['name']}", BRIGHT_YELLOW + BOLD)
    )
    out(colorize(f"{state['game_state']['duration']}", DIM + BOLD))

    draw_line("═")
