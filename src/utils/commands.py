"""Grouped Available Commands table (rich Table, plaintext fallback)."""
HELP_COMMANDS: list[tuple[str, list[tuple[str, str, str]]]] = [
    ("Movement", [
        ("go <direction|room>", "Move (n/s/e/w or adjacent room name)",
         "go north, go lab"),
        ("look", "Re-render current room", "look"),
    ]),
    ("Inspect & Items", [
        ("inspect <target>", "Examine object or item", "inspect desk"),
        ("take <item>", "Pick up item", "take battery_pack"),
        ("use <item> on <target>", "Use item / solve puzzle", "use 2015 on desk"),
        ("inventory", "Show carried items (inv, i)", "inventory"),
    ]),
    ("System", [
        ("save \\[slot]", "Save game", "save"),
        ("load \\[slot]", "Load game", "load"),
        ("clear (cls)", "Clear screen", "clear"),
        ("help (?, h)", "Show this help", "help"),
        ("quit (q, exit)", "Quit game", "quit"),
    ]),
]