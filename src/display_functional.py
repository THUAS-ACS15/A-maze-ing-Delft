from subprocess import run

from .state_functional import state

def colorize(text: str, color_code: str) -> str:
    return f"{color_code}{text}\033[0m" if state["enable_colors"] else text

def out(text: str = "") -> None:
    import builtins

    builtins.print(safe(text))

def draw_line(char: str = "-") -> None:
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
