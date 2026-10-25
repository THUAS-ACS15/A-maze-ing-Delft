"""Tests for ``src/parser.py``."""

import pytest

import src.parser as parser


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("  LOBBY  ", "lobby", id="strip-and-lower"),
        pytest.param("Teachers_Room_1", "teachers room 1", id="underscores"),
        pytest.param("CLASSROOM  D  2015", "classroom d 2015", id="collapse-spaces"),
        pytest.param("", "", id="empty"),
        pytest.param("   ", "", id="whitespace-only"),
        pytest.param("d2001", "d2001", id="already-normalized"),
    ],
)
def test_normalize_room_key(raw, expected):
    assert parser.normalize_room_key(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("north", "north", id="direction"),
        pytest.param("N", "north", id="direction-alias"),
        pytest.param("east", "east", id="direction-long"),
        pytest.param("lobby", "lobby", id="room-name"),
        pytest.param("d2015", "classroom_d_2015", id="room-alias"),
        pytest.param("D  2015", "classroom_d_2015", id="normalized-room-alias"),
        pytest.param("teachers room 1", "teachers_room_1", id="multiword-room"),
        pytest.param("lab_d2_001", "lab_d2_001", id="underscored-fallback"),
        pytest.param("some unknown room", "some_unknown_room", id="unknown-fallback"),
    ],
)
def test_resolve_room_target(raw, expected):
    assert parser.resolve_room_target(raw) == expected


def test_resolve_room_target_precedence(monkeypatch):
    monkeypatch.setattr(parser, "ROOM_ALIASES", {"north": "north", "n": "north"})
    monkeypatch.setattr(
        parser, "ROOM_NAME_ALIASES", {"lobby": "lobby", "floor lobby": "lobby"}
    )

    assert parser.resolve_room_target("north") == "north"
    assert parser.resolve_room_target("n") == "north"
    assert parser.resolve_room_target("lobby") == "lobby"
    assert parser.resolve_room_target("floor lobby") == "lobby"
    assert parser.resolve_room_target("hall") == "hall"


@pytest.mark.parametrize(
    "raw_input",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace-only"),
    ],
)
def test_parse_empty(raw_input):
    assert parser.parse(raw_input) == ("EMPTY", {})


@pytest.mark.parametrize(
    ("raw_input", "expected_raw"),
    [
        pytest.param("fly to the moon", "fly to the moon", id="multiword"),
        pytest.param("xyzzy", "xyzzy", id="single-token"),
        pytest.param("  Fly  ", "  Fly  ", id="original-raw-preserved"),
    ],
)
def test_parse_unknown_verb(raw_input, expected_raw):
    assert parser.parse(raw_input) == ("UNKNOWN", {"raw": expected_raw})


@pytest.mark.parametrize(
    ("raw_input", "expected_target"),
    [
        pytest.param("north", "north", id="direction"),
        pytest.param("n", "north", id="direction-alias"),
        pytest.param("lobby", "lobby", id="room-name"),
        pytest.param("d2015", "classroom_d_2015", id="room-alias"),
    ],
)
def test_parse_single_token_movement(raw_input, expected_target):
    assert parser.parse(raw_input) == (
        "go",
        {"target": expected_target, "raw": raw_input},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("back", "back", "back", id="back"),
        pytest.param("backward", "back", "backward", id="backward"),
        pytest.param("bkw", "back", "bkw", id="bkw"),
        pytest.param("behind", "back", "behind", id="behind"),
        pytest.param("forward", "forward", "forward", id="forward"),
        pytest.param("front", "forward", "front", id="front"),
        pytest.param("fwd", "forward", "fwd", id="fwd"),
        pytest.param("go back", "back", "back", id="go-back"),
        pytest.param("move forward", "forward", "forward", id="move-forward"),
    ],
)
def test_parse_history_movement(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "go",
        {"target": expected_target, "raw": expected_raw},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_action", "expected_raw"),
    [
        pytest.param("look", "look", "", id="look"),
        pytest.param("l", "look", "", id="look-alias"),
        pytest.param("look around", "look", "around", id="look-with-arg"),
        pytest.param("inventory", "inventory", "", id="inventory"),
        pytest.param("i", "inventory", "", id="inventory-alias"),
        pytest.param("help", "help", "", id="help"),
        pytest.param("h", "help", "", id="help-alias"),
        pytest.param("?", "help", "", id="help-question"),
        pytest.param("quit", "quit", "", id="quit"),
        pytest.param("q", "quit", "", id="quit-alias"),
        pytest.param("activate", "activate", "", id="activate"),
        pytest.param("power on", "activate", "on", id="activate-alias-with-arg"),
    ],
)
def test_parse_simple_verbs(raw_input, expected_action, expected_raw):
    assert parser.parse(raw_input) == (expected_action, {"raw": expected_raw})


@pytest.mark.parametrize(
    ("raw_input", "expected_slot", "expected_raw"),
    [
        pytest.param("save", None, "", id="default-slot"),
        pytest.param("save slot1", "slot1", "slot1", id="explicit-slot"),
    ],
)
def test_parse_save(raw_input, expected_slot, expected_raw):
    assert parser.parse(raw_input) == (
        "save",
        {"target": expected_slot, "raw": expected_raw},
    )


def test_parse_register_with_name():
    assert parser.parse("register alice") == (
        "register",
        {"target": "alice", "raw": "alice"},
    )


def test_parse_register_without_name_uses_generator(monkeypatch):
    monkeypatch.setattr(parser, "random_name_generator", lambda: "Operator_Aegis_123")

    assert parser.parse("register") == (
        "register",
        {"target": "Operator_Aegis_123", "raw": ""},
    )


def test_parse_saves():
    assert parser.parse("saves") == ("saves", {"raw": ""})


@pytest.mark.parametrize(
    ("raw_input", "expected_slot", "expected_raw"),
    [
        pytest.param("load slot1", "slot1", "slot1", id="explicit-slot"),
    ],
)
def test_parse_load(raw_input, expected_slot, expected_raw):
    assert parser.parse(raw_input) == (
        "load",
        {"target": expected_slot, "raw": expected_raw},
    )


def test_parse_load_without_slot_is_invalid():
    assert parser.parse("load") == (
        "INVALID",
        {"message": "Enter a valid slot to load (e.g., 'load user_slot_1')."},
    )


@pytest.mark.parametrize(
    "raw_input",
    [
        pytest.param("login alice", id="login"),
        pytest.param("log_in alice", id="log-in-underscore"),
        pytest.param("sign_in alice", id="sign-in-underscore"),
    ],
)
def test_parse_login(raw_input):
    assert parser.parse(raw_input) == (
        "login",
        {"target": "alice", "raw": "alice"},
    )


def test_parse_login_without_name_is_invalid():
    assert parser.parse("login") == (
        "INVALID",
        {"message": "You have to enter a valid username (e.g., 'login user1')."},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("go north", "north", "north", id="direction"),
        pytest.param("go lobby", "lobby", "lobby", id="room-name"),
        pytest.param("go d2015", "classroom_d_2015", "d2015", id="room-alias"),
        pytest.param("move south", "south", "south", id="move-alias"),
    ],
)
def test_parse_go(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "go",
        {"target": expected_target, "raw": expected_raw},
    )


def test_parse_go_no_args():
    assert parser.parse("go") == (
        "INVALID",
        {
            "message": (
                "Go where? Specify a direction (north, south, east, west) "
                "or room name."
            )
        },
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_raw"),
    [
        pytest.param("restart", "", id="restart"),
        pytest.param("new_game", "", id="new-game-underscore"),
    ],
)
def test_parse_restart(raw_input, expected_raw):
    assert parser.parse(raw_input) == ("restart", {"raw": expected_raw})


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("inspect desk", "desk", "desk", id="object"),
        pytest.param("inspect battery", "battery_pack", "battery", id="item-alias"),
        pytest.param("x keycard", "keycard_lvl1", "keycard", id="verb-alias"),
    ],
)
def test_parse_inspect(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "inspect",
        {"target": expected_target, "raw": expected_raw},
    )


def test_parse_inspect_no_args():
    assert parser.parse("inspect") == (
        "INVALID",
        {"message": "Inspect what? Specify an item or object (e.g., 'inspect desk')."},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("take battery", "battery_pack", "battery", id="take"),
        pytest.param("get keycard", "keycard_lvl1", "keycard", id="get-alias"),
        pytest.param(
            "grab chassis frame", "chassis_frame", "chassis frame", id="multiword"
        ),
    ],
)
def test_parse_take(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "take",
        {"target": expected_target, "raw": expected_raw},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("pick up battery", "battery_pack", "battery", id="single-item"),
        pytest.param(
            "pick up chassis frame", "chassis_frame", "chassis frame", id="multiword"
        ),
    ],
)
def test_parse_pick_up(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "take",
        {"target": expected_target, "raw": expected_raw},
    )


def test_parse_take_no_args():
    assert parser.parse("take") == (
        "INVALID",
        {"message": "Take what? Specify an item (e.g., 'take battery_pack')."},
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_indirect", "expected_raw"),
    [
        pytest.param(
            "use keycard on door",
            "keycard_lvl1",
            "door",
            "keycard on door",
            id="on",
        ),
        pytest.param(
            "use keycard with door",
            "keycard_lvl1",
            "door",
            "keycard with door",
            id="with",
        ),
        pytest.param(
            "put battery onto workbench",
            "battery_pack",
            "workbench",
            "battery onto workbench",
            id="onto",
        ),
        pytest.param(
            "place chassis_frame in slot",
            "chassis_frame",
            "slot",
            "chassis_frame in slot",
            id="in",
        ),
    ],
)
def test_parse_use_with_indirect(
    raw_input, expected_target, expected_indirect, expected_raw
):
    assert parser.parse(raw_input) == (
        "use",
        {
            "target": expected_target,
            "indirect": expected_indirect,
            "raw": expected_raw,
        },
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_target", "expected_raw"),
    [
        pytest.param("use keycard", "keycard_lvl1", "keycard", id="single-item"),
        pytest.param(
            "install chassis_frame", "chassis_frame", "chassis_frame", id="install"
        ),
        pytest.param("use battery pack", "battery_pack", "battery pack", id="multiword"),
    ],
)
def test_parse_use_without_indirect(raw_input, expected_target, expected_raw):
    assert parser.parse(raw_input) == (
        "use",
        {"target": expected_target, "indirect": None, "raw": expected_raw},
    )


def test_parse_use_no_args():
    assert parser.parse("use") == (
        "INVALID",
        {
            "message": (
                "Use what? Syntax: 'use <item>' or 'use <item> on <target>'."
            )
        },
    )


@pytest.mark.parametrize(
    ("raw_input", "expected_raw"),
    [
        pytest.param("clear", "", id="no-args"),
        pytest.param("clear screen", "screen", id="with-args"),
    ],
)
def test_parse_clear_verb(monkeypatch, raw_input, expected_raw):
    # Real aliases map "clear" to "look", so the clear branch is unreachable
    # without replacing the verb table.
    monkeypatch.setattr(parser, "VERB_ALIASES", {"clear": "clear"})

    assert parser.parse(raw_input) == ("clear", {"raw": expected_raw})


@pytest.mark.parametrize(
    ("raw_input", "expected_raw"),
    [
        pytest.param("drop battery", "drop battery", id="drop"),
    ],
)
def test_parse_unhandled_verb_falls_through(raw_input, expected_raw):
    # This verb exists in VERB_ALIASES but has no handling branch.
    assert parser.parse(raw_input) == ("UNKNOWN", {"raw": expected_raw})
