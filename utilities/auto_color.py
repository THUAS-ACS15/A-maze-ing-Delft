import builtins
from itertools import cycle

COLORS = {
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "magenta": "\033[95m",
    "blue": "\033[94m",
    "red": "\033[91m",
    "reset": "\033[0m"
}

dialogue_color_cycle = cycle(["cyan", "yellow", "magenta", "blue"])
_original_print = builtins.print

def auto_color_print(*args, **kwargs):
    if not args:
        _original_print(**kwargs)
        return

    text_str = " ".join(str(arg) for arg in args)

    if any(w in text_str.lower() for w in ["wrong", "locked", "invalid", "error", "danger"]):
        color = "red"
    elif text_str.strip().startswith(("[", "1", "2", "3", "4", "(")) or "?" in text_str:
        color = "green"
    else:
        color = next(dialogue_color_cycle)

    _original_print(f"{COLORS[color]}{text_str}{COLORS['reset']}", **kwargs)

# This line turns it on automatically as soon as this file is loaded!
builtins.print = auto_color_print