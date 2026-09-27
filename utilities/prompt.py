from rich.console import Console
from rich.prompt import Prompt

def prompt(console: Console, choices: list, default: str = "") -> str:
    """Ask for a command with the project's prompt configuration."""
    return Prompt.ask(choices=choices, show_choices=False, console=console)