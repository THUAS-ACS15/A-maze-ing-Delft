# ruff: noqa: E402 -- project root must be added to sys.path before these imports.
# -----------------------------------------------------------------------------
# File: test_display_menu.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

# ^ prevent ruff from erroring imports
# because pytest needs that path before importing (as below)

import sys
from io import StringIO
from pathlib import Path

from rich.console import Console

# add absolute root path to the system path so that pytest can run
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))

from utilities import display_menu


def test_render_command_options_renders_correctly(monkeypatch):
	"""Render the selected command with its description and marker."""
	output = StringIO()
	console = Console(file=output, force_terminal=False)

	monkeypatch.setattr(display_menu, "clear_screen", lambda *args: None)

	display_menu.render_command_options(
		console,
		selected_index=1,
		command_desc="Choose a destination",
		commands=["lobby", "corridor_east"],
	)

	text = output.getvalue()
	assert "Choose a destination" in text
	assert "Lobby" in text
	assert "> corridor_east" in text


def test_render_command_options_aligns_correctly(monkeypatch):
	"""Align command names and descriptions in fixed-width columns."""
	output = StringIO()
	console = Console(file=output, force_terminal=False)

	monkeypatch.setattr(display_menu, "clear_screen", lambda *args: None)

	display_menu.render_command_options(
		console,
		selected_index=0,
		command_desc="Available actions",
		commands={"look": "Inspect the room", "inventory": "View your items"},
	)

	lines = output.getvalue().splitlines()
	assert lines[1] == " > look      : Inspect the room"
	assert lines[2] == "   inventory : View your items"


def test_display_selection_menu_moves_and_returns_correctly(monkeypatch):
	"""Move through the selection menu and return the highlighted option."""
	rendered_selections = []
	keys = iter(["down", "up", "enter"])

	monkeypatch.setattr(
		display_menu,
		"render_command_options",
		lambda console, selected, command_desc, options: rendered_selections.append(selected),
	)
	monkeypatch.setattr(display_menu, "read_key", lambda: next(keys))
	monkeypatch.setattr(display_menu, "clear_screen", lambda *args: None)

	selected = display_menu.display_selection_menu(
		"Choose an action",
		["look", "inventory"],
	)

	assert rendered_selections == [0, 1, 0]
	assert selected == "look"


def test_display_menu_lists_command_descriptions():
	"""List every command with its description in the menu output."""
	output = StringIO()
	console = Console(file=output, force_terminal=False)

	display_menu.display_menu(
		console,
		{"look": "Inspect the room", "inventory": "View your items"},
	)

	lines = output.getvalue().splitlines()
	assert lines[0] == "List of all available commands for this room"
	assert lines[1] == "   look                 : Inspect the room"
	assert lines[2] == "   inventory            : View your items"
