"""Tests for ``src/rooms/teachers_room_1.py``."""

import pytest

from src.rooms import teachers_room_1


def test_wrong_target(desk, desk_code, render_text):
    teachers_room_1.use_desk_code(desk_code.lower(), target="window")

    assert render_text(desk["render"]) == "Nothings happens"
    assert desk["state"]["flags"]["tr1_desk_unlocked"] is False
    assert desk["state"]["player"]["inventory"] == []


def test_already_unlocked(desk, desk_code, render_text):
    desk["state"]["flags"]["tr1_desk_unlocked"] = True

    teachers_room_1.use_desk_code(desk_code.lower())

    assert render_text(desk["render"]) == "The desk is already unlocked."


@pytest.mark.parametrize("target", [None, "desk"])
def test_correct_code_unlocks_and_rewards(desk, target, desk_code, reward,
                                          render_text):
    teachers_room_1.use_desk_code(desk_code.lower(), target=target)

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is True
    assert desk["state"]["player"]["inventory"] == [reward]
    assert "obtained the Level-1 Staff Keycard" in render_text(desk["render"])


def test_correct_code_reward_already_owned(desk, desk_code, reward, render_text):
    desk["state"]["player"]["inventory"] = [reward]

    teachers_room_1.use_desk_code(desk_code.lower())

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is True
    assert desk["state"]["player"]["inventory"] == [reward]
    assert (
        render_text(desk["render"])
        == "You already have a Level-1 Staff keycard."
    )


@pytest.mark.parametrize("item", ["0000", "D2084", "d208", ""])
def test_incorrect_code(desk, item, render_text):
    teachers_room_1.use_desk_code(item)

    assert f"Incorrect code entered.: {item}" in render_text(desk["render"])
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
def test_code_matching_case(desk, code, item, expects_unlock, reward,
                            render_text):
    desk["state"]["rooms"]["teachers_room_1"]["interactables"]["desk"]["code"] = code

    teachers_room_1.use_desk_code(item)

    assert desk["state"]["flags"]["tr1_desk_unlocked"] is expects_unlock
    if expects_unlock:
        assert desk["state"]["player"]["inventory"] == [reward]
    else:
        assert desk["state"]["player"]["inventory"] == []
