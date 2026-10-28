from pathlib import Path
from dotenv import load_dotenv
from src.state import init as state_init
from db import init as db_init


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

db_init()
state_init()