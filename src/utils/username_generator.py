"""Generate unique, human-readable usernames for new players."""

import random

from db import connection

PREFIXES = ["Operator", "Cyber", "Null", "Cipher", "Agent", "Ghost", "Vector", "Node"]
CALLSIGNS = ["Aegis", "Vex", "Echo", "Kilo", "Zero", "Nexus", "Drift", "Sol"]


def generate_random_username() -> str:
    """Generates a random username and verifies it does not exist in the database."""
    with connection() as conn:
        while True:
            # 1. Build a candidate username
            prefix = random.choice(PREFIXES)
            callsign = random.choice(CALLSIGNS)
            suffix = random.randint(100, 999)
            candidate = f"{prefix}_{callsign}_{suffix}"

            # 2. Check SQLite DB for existence
            cur = conn.execute("SELECT 1 FROM users WHERE name = ?", (candidate,))
            if cur.fetchone() is None:
                return candidate
