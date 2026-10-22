from pathlib import Path
from dotenv import load_dotenv
from src.state import initialize


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

initialize()