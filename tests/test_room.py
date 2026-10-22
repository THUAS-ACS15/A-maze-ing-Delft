"""Tests for ``src/room.py``'s ``render()`` output."""

import copy

import pytest

import src.state as state_module
from src import room

BASE_STATE = {
    "enable_colors": False,
    "terminal_width": 20,
    "player": {"current_room": "lab"},
    "game_state": {"phase": "EXPLORATION", "duration": "00:00:00"},
    "rooms": {
        "lab": {
            "name": "Lab",
            "description": "A test lab.",
            "exits": {"east": "hall"},
            "items": [],
            "interactables": {},
        }
    },
    "items": {},
}


@pytest.fixture
def room_state(monkeypatch):
    """Patch both state bindings that ``render()`` relies on.

    ``room.render()`` reads the module-level ``room.state`` import, while the
    ``display`` helpers resolve ``src.state.state`` freshly on each call.
    Patching both to the same dict keeps them consistent.
    """
    state = copy.deepcopy(BASE_STATE)
    monkeypatch.setattr(room, "state", state)
    monkeypatch.setattr(state_module, "state", state)
    return state


def test_render_basic(room_state, capsys):
    room_state["rooms"]["lab"]["items"] = ["battery"]
    room_state["rooms"]["lab"]["interactables"] = {"workbench": {}}
    room_state["items"]["battery"] = {
        "name": "Battery Pack",
        "is_assembly_part": True,
    }

    room.render()

    output = capsys.readouterr().out
    assert "[EXPLORATION]" in output
    assert "LOCATION: Lab" in output
    assert "00:00:00" in output
    assert "A test lab." in output
    assert "Exits: EAST -> hall" in output
    assert "Items in area:" in output
    assert "Battery Pack" in output
    assert "[ASSEMBLY PART]" in output
    assert "Interactive Objects:" in output
    assert "workbench" in output


def test_render_custom_text(room_state, capsys):
    room.render(text="CUSTOM NARRATIVE")

    output = capsys.readouterr().out
    assert "CUSTOM NARRATIVE" in output
    assert "A test lab." not in output


def test_render_prints_asset(room_state, capsys):
    room.render(asset="<ASCII ART>")

    assert "<ASCII ART>" in capsys.readouterr().out


@pytest.mark.parametrize(
    "exits",
    [
        pytest.param(None, id="missing-exits-key"),
        pytest.param({}, id="empty-exits"),
    ],
)
def test_render_no_exits(room_state, capsys, exits):
    if exits is None:
        del room_state["rooms"]["lab"]["exits"]
    else:
        room_state["rooms"]["lab"]["exits"] = exits

    room.render()

    assert "Exits: None available." in capsys.readouterr().out


@pytest.mark.parametrize(
    ("item_def", "expected_name", "expect_tag"),
    [
        pytest.param(
            {"name": "Battery Pack", "is_assembly_part": True},
            "Battery Pack",
            True,
            id="assembly-part",
        ),
        pytest.param(
            {"name": "Battery Pack", "is_assembly_part": False},
            "Battery Pack",
            False,
            id="not-assembly-part",
        ),
        pytest.param(
            {"name": "Battery Pack"},
            "Battery Pack",
            False,
            id="missing-flag",
        ),
        pytest.param(
            {"is_assembly_part": True},
            "battery",
            True,
            id="missing-name-falls-back-to-id",
        ),
    ],
)
def test_render_items(room_state, capsys, item_def, expected_name, expect_tag):
    room_state["rooms"]["lab"]["items"] = ["battery"]
    room_state["items"]["battery"] = item_def

    room.render()

    output = capsys.readouterr().out
    assert expected_name in output
    assert ("[ASSEMBLY PART]" in output) is expect_tag


@pytest.mark.parametrize(
    ("room_extra", "expected_key", "expect_section"),
    [
        pytest.param(
            {"interactables": {"workbench": {}}},
            "workbench",
            True,
            id="interactables",
        ),
        pytest.param(
            {"interactable": {"desk": {}}},
            "desk",
            True,
            id="interactable-singular-fallback",
        ),
        pytest.param({}, None, False, id="no-interactables"),
    ],
)
def test_render_interactables(
    room_state, capsys, room_extra, expected_key, expect_section
):
    room_data = room_state["rooms"]["lab"]
    room_data.pop("interactables", None)
    room_data.pop("interactable", None)
    room_data.update(room_extra)

    room.render()

    output = capsys.readouterr().out
    assert ("Interactive Objects:" in output) is expect_section
    if expected_key is not None:
        assert expected_key in output


def test_render_no_items(room_state, capsys):
    room.render()

    assert "Items in area:" not in capsys.readouterr().out
