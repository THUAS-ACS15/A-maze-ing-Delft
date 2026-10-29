"""ANSI escape sequences for terminal colours and styles, plus semantic aliases (ERROR, SUCCESS, ...)."""

BLACK = "\033[30m"
RED = "\033[31m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# High-Intensity Colors
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

ERROR = BRIGHT_RED
SUCCESS = BRIGHT_GREEN
WARNING = BRIGHT_YELLOW
INFO = BRIGHT_BLUE

BOLD = "\033[1m"
RESET = "\033[0m"