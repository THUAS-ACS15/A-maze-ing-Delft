import pyfiglet
from rich.console import Console
from rich.text import Text

console = Console()

# Generate the ASCII art text string (e.g., using the 'block' font)
ascii_text = pyfiglet.figlet_format("TERMINAL", font="")

# Print it using Rich with custom colors/styles
console.print(Text(ascii_text, style="bold cyan"))