"""Process-wide configuration and start-up side effects.

Importing this module has side effects by design: it loads environment variables from ``.env`` (API keys for the
chat providers), creates the SQLite schema via :func:`db.init`, and loads the game state via
:func:`src.state.init`.

Attributes:
    PROJECT_ROOT: Absolute path of the repository root (the directory containing this file).
"""

from pathlib import Path
from dotenv import load_dotenv
from src.state import init as state_init
from db import init as db_init


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

db_init()
state_init()