# -----------------------------------------------------------------------------
# File: test_inventory_viewer.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: October 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from rich.text import Text

import sys
from pathlib import Path

# add absolute root path to the system path so that pytest can run
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))

# import the whole file as a module
import utilities.inventory_viewer as inventory_viewer

# tests for: inventory_viewer.py

def test_create_list_panel_highlights_selected_item() -> None:
	panel = inventory_viewer.create_list_panel(["key", "map"], selected=1, panel_height=6)

	assert panel.title == "[bold]Items[/bold]"
	assert isinstance(panel.renderable, Text)
	assert panel.renderable.plain == "    key\n  > map\n\n\n"
	selected_offset = panel.renderable.plain.index("> map")
	assert any(
		span.style == "bold green" and span.start <= selected_offset < span.end
		for span in panel.renderable.spans
	)


def test_create_list_panel_scrolls_correctly():
	inventory = [f"item-{index}" for index in range(8)]

	panel = inventory_viewer.create_list_panel(inventory, selected=6, panel_height=5)

	assert isinstance(panel.renderable, Text)
	assert panel.renderable.plain == "    item-5\n  > item-6\n    item-7\n"


def test_create_item_details_panel_uses_known_item_data():
	item_name = next(iter(inventory_viewer.item_description_bank))

	panel = inventory_viewer.create_item_details_panel(item_name, panel_height=20)

	assert panel.title == f"[bold]{item_name}[/bold]"
	assert panel.renderable.renderables[1].renderable == inventory_viewer.item_description_bank[item_name]


def test_create_item_details_uses_fallback_for_missing_item():
	panel = inventory_viewer.create_item_details_panel("missing item", panel_height=20)

	assert panel.title == "[bold]missing item[/bold]"
	assert panel.renderable.renderables[0].renderable.renderable == inventory_viewer.NO_RENDER_PLACEHOLDER
	assert panel.renderable.renderables[1].renderable == "No description available."


def test_create_item_details_handles_empty_selection():
	panel = inventory_viewer.create_item_details_panel(None, panel_height=20)

	assert panel.title == "[dim]No item selected[/dim]"
	assert panel.renderable.renderables[1].renderable == "No description available."


def test_display_inventory_moves_selection(monkeypatch):
	# monkeypatch is used here to simulate a keypress using read_key
	rendered_selections: list[int] = []
	keys = iter(["down", "up", "enter"])

	monkeypatch.setattr(
		inventory_viewer,
		"render_inventory",
		lambda console, inventory, selected: rendered_selections.append(selected),
	)
	monkeypatch.setattr(inventory_viewer, "read_key", lambda: next(keys))

	inventory_viewer.display_inventory(["key", "map"])

	assert rendered_selections == [0, 1, 0]
