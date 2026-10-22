"""Tests for ``src/rooms/teachers_room_1.py``."""

from unittest.mock import Mock

import pytest

from src.rooms import teachers_room_1

DESK_CODE = "D2084"
REWARD = "keycard_lvl1"


def _rendered_text(render_mock: Mock) -> str:
    """Return the text passed to the mocked ``render(text=...)`` call."""
    return render_mock.call_args.kwargs["text"]


@pytest.fixture
def desk(monkeypatch):
    state = {
        "rooms": {
            "teachers_room_1": {
                "interactables": {"desk": {"code": DESK_CODE, "reward": REWARD}}
            }
        },
        "flags": {"tr1_desk_unlocked": False},
        "player": {"inventory": []},
    }
    render_mock = Mock()
    monkeypatch.setattr(teachers_room_1, "state", state)
    monkeypatch.setattr(teachers_room_1, "render", render_mock)
    monkeypatch.setattr(
        teachers_room_1, "colorize", lambda text, color_code=None: text
    )
    return {"state": state, "render": render_mock}


def test_wrong_target(desk):
    teachers_room_1.use_desk_code(DESK_CODE.lower(), target="window")

    assert _rendered_text(desk["render"]) == "Nothings happens"
    assert desk["state"]["flags"]["tr1_desk_unlocked"] is False
    assert desk["state"]["player"]["inventory"] == []


def test_already_unlocked(desk):
    desk["state"]["flags"]["tr1_desk_unlocked"] = True

    teachers_room_1.use_desk_code(DESK_CODE.lower())

    assert _rendered_text(desk["render"]) == "The desk is already unlocked."


@pytest.mark.parametrize("target", [None, "desk"])
def test_correct_code_unlocks_and_rewards(desk, target):
    teachers_room_1.use_desk_code(DESK_CODE.lower(), target=target)

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is True
    assert desk["state"]["player"]["inventory"] == [REWARD]
    assert "obtained the Level-1 Staff Keycard" in _rendered_text(desk["render"])


def test_correct_code_reward_already_owned(desk):
    desk["state"]["player"]["inventory"] = [REWARD]

    teachers_room_1.use_desk_code(DESK_CODE.lower())

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is True
    assert desk["state"]["player"]["inventory"] == [REWARD]
    assert (
        _rendered_text(desk["render"])
        == "You already have a Level-1 Staff keycard."
    )


@pytest.mark.parametrize("item", ["0000", DESK_CODE, "d208", ""])
def test_incorrect_code(desk, item):
    teachers_room_1.use_desk_code(item)

    assert f"Incorrect code entered.: {item}" in _rendered_text(desk["render"])
    assert desk["state"]["flags"]["tr1_desk_unlocked"] is False
    assert desk["state"]["player"]["inventory"] == []


@pytest.mark.parametrize(
    ("code", "item", "expects_unlock"),
    [
        pytest.param("D2084", "d2084", True, id="lowercase-item-matches"),
        pytest.param("D2084", "D2084", False, id="uppercase-item-does-not-match"),
        pytest.param("1234", "1234", True, id="digits-unaffected"),
    ],
)
def test_code_matching_case(desk, code, item, expects_unlock):
    desk["state"]["rooms"]["teachers_room_1"]["interactables"]["desk"]["code"] = code

    teachers_room_1.use_desk_code(item)

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is expects_unlock
    if expects_unlock:
        assert desk["state"]["player"]["inventory"] == [REWARD]
    else:
        assert desk["state"]["player"]["inventory"] == []
