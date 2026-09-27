from rich.console import Console
from rich.text import Text
import time

def print_line(console: Console, text: str, style: str = "", delay: float = 0.015) -> None:
    """Print one styled line, pausing briefly to keep the streaming feel."""
    console.print(Text(text, style=style or ""))
    if delay > 0:
        time.sleep(delay * 10)