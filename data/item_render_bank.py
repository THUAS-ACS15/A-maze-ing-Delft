# -----------------------------------------------------------------------------
# File: item_render_bank.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# Contributors: Leon
# -----------------------------------------------------------------------------
"""ASCII art renders for inventory items."""


item_render_bank: dict[str, str] = {
	# Compact terminal renders: each combines a small label with an item silhouette.
	"Robot Chassis Frame": r"""
╔════════════════╗
║                ║
║  ◉          ◉  ║
║      ────      ║
║                ║
╚════════════════╝""",

	"Wi-Fi Credentials": r"""
┌──────────────────┐
│    Credentials   │
│                  │
│     SSID  •••    │
│    PASS  •••••   │
└──────────────────┘""",

	"Encrypted API & Prompt USB": r"""
        ┌────────┐
   ─────┤  USB3  ├───┐
        └────────┘   │
          ▣▣▣▣       └─┐
""",

	"Makeshift Mic and Speaker Combo": r"""
 .──────.     ╭──╮
/   \/   \─────│)│
 '──────'     ╰──╯
╲________/
""",

	"A.I.G.I.S. Motherboard": r"""
┌─────┐  ╔═══════╗
│ CPU │──║ ▦ ▦ ▦ ║
└─────┘  ╚═══════╝
▪ ▪  ───────  ▪ ▪
""",

	"Memory Sticks": r"""
┌──────────────┐
│ DDR   ▪ ▪ ▪  │
├──────────────┤
│ DDR   ▪ ▪ ▪  │
└──────────────┘""",

	"Student ID card": r"""
┌────────────────────┐
│ STUDENT ID         │
│  ┌───┐  NAME: YOU  │
│  │ ◉ │  THUAS      │
│  └───┘  ID ▰▰▰▰    │
└────────────────────┘""",

	"Staff Keycard": r"""
┌────────────────────┐
│ STAFF KEYCARD      │
│  ┌───┐  ACCESS: ✓  │
│  │▦▦▦│  THUAS      │
│  └───┘  ▰▰▰▰▰      │
└────────────────────┘""",

	"Quiz certificate": r"""
┌────────────────────┐
│  QUIZ CERTIFICATE  │
│                    │
│    good job! you   │
│       passed       │
└────────────────────┘""",
}
