import re

def next_save_slot(name: str) -> str:
    """Return the next unused auto-save slot for ``name``."""
    from src.state import SAVE_DIR

    prefix = f"{name}_save_slot_"
    numbers = []
    if SAVE_DIR.exists():
        for path in SAVE_DIR.glob(f"{prefix}*.json"):
            match = re.fullmatch(rf"{re.escape(prefix)}(\d+)\.json", path.name)
            if match:
                numbers.append(int(match.group(1)))
    return f"{prefix}{max(numbers, default=0) + 1}"