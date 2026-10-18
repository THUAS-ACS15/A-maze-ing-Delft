from subprocess import run

ENABLE_COLORS: bool = True
TERMINAL_WIDTH: int = 80

def init():
    global ENABLE_COLORS, TERMINAL_WIDTH
    ENABLE_COLORS = ENABLE_COLORS
    TERMINAL_WIDTH = TERMINAL_WIDTH

def colorize(text: str, color_code: str) -> str:
    return f"{color_code}{text}\033[0m" if ENABLE_COLORS else text

def out(text: str = "") -> None:
    import builtins

    builtins.print(safe(text))

def draw_line(char: str = "-") -> None:
    out(colorize(char * TERMINAL_WIDTH, "\033[2m"))

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
