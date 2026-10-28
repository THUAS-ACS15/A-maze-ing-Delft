"""Tests for ``src/display.py``."""

import builtins
import os
from unittest.mock import Mock

import pytest

import src.display as display
import src.state as state_module


def _block_rich_import(monkeypatch):
    """Simulate rich not being installed for clear()'s fallback path."""
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "rich.console":
            raise ModuleNotFoundError("No module named 'rich.console'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("hello world", "hello world", id="ascii"),
        pytest.param("", "", id="empty"),
        pytest.param("─═•→←", "-=*-><-", id="box-chars"),
        pytest.param("Room ─ Lab", "Room - Lab", id="mixed"),
        pytest.param("你好", "??", id="non-cp1252-replaced"),
        pytest.param("café", "café", id="cp1252-passthrough"),
        pytest.param("• 你好 →", "* ?? ->", id="mixed-non-cp1252"),
    ],
)
def test_safe(text, expected):
    assert display.safe(text) == expected


@pytest.mark.parametrize(
    ("enable_colors", "expected"),
    [
        pytest.param(True, "REDhello\033[0m", id="colors-on"),
        pytest.param(False, "hello", id="colors-off"),
    ],
)
def test_colorize(monkeypatch, enable_colors, expected):
    monkeypatch.setattr(state_module, "state", {"enable_colors": enable_colors})

    assert display.colorize("hello", "RED") == expected


def test_out_prints_text(capsys):
    display.out("hello")

    assert capsys.readouterr().out == "hello\n"


def test_out_default_empty(capsys):
    display.out()

    assert capsys.readouterr().out == "\n"


def test_out_translates_box_chars(capsys):
    display.out("═")

    assert capsys.readouterr().out == "=\n"


def test_draw_line_custom_char(monkeypatch):
    monkeypatch.setattr(
        state_module, "state", {"enable_colors": False, "terminal_width": 5}
    )
    out_mock = Mock()
    monkeypatch.setattr(display, "out", out_mock)

    display.draw_line("*")

    out_mock.assert_called_once_with("*****")


def test_draw_line_default_char(monkeypatch):
    monkeypatch.setattr(
        state_module, "state", {"enable_colors": False, "terminal_width": 3}
    )
    out_mock = Mock()
    monkeypatch.setattr(display, "out", out_mock)

    display.draw_line()

    out_mock.assert_called_once_with("---")


def test_clear_uses_rich_console(monkeypatch):
    console_cls = Mock()
    monkeypatch.setattr("rich.console.Console", console_cls)

    display.clear()

    console_cls.return_value.clear.assert_called_once()


def test_clear_pycharm_fallback(monkeypatch, capsys):
    _block_rich_import(monkeypatch)
    monkeypatch.setenv("PYCHARM_HOSTED", "1")

    display.clear()

    assert capsys.readouterr().out == "\n" * 51


@pytest.mark.parametrize(
    ("os_name", "expected_cmd"),
    [
        pytest.param("nt", "cls", id="windows"),
        pytest.param("posix", "clear", id="posix"),
    ],
)
def test_clear_subprocess_fallback(monkeypatch, os_name, expected_cmd):
    _block_rich_import(monkeypatch)
    monkeypatch.delenv("PYCHARM_HOSTED", raising=False)
    monkeypatch.setattr(os, "name", os_name)
    run_mock = Mock()
    monkeypatch.setattr(display, "run", run_mock)

    display.clear()

    run_mock.assert_called_once_with([expected_cmd], shell=True)


def test_header_reads_state_and_draws(monkeypatch):
    monkeypatch.setattr(
        state_module,
        "state",
        {
            "enable_colors": False,
            "terminal_width": 10,
            "player": {"current_room": "lab", "name": "guest"},
            "rooms": {"lab": {"name": "Lab D 2001"}},
            "game_state": {
                "phase": "EXPLORATION",
                "duration": {
                    "last_write": None,
                    "value": "00:05:00",
                    "pause": False,
                },
            },
        },
    )
    monkeypatch.setattr(display, "colorize", lambda text, color_code: text)
    out_mock = Mock()
    draw_mock = Mock()
    monkeypatch.setattr(display, "out", out_mock)
    monkeypatch.setattr(display, "draw_line", draw_mock)

    display.header()

    assert draw_mock.call_count == 2
    assert [call.args[0] for call in draw_mock.call_args_list] == ["═", "═"]
    assert out_mock.call_count == 5
    assert [call.args[0] for call in out_mock.call_args_list] == [
        "[EXPLORATION]",
        "LOCATION: Lab D 2001",
        "GUEST",
        "00:05:00",
        "",
    ]


def test_header_with_content(monkeypatch):
    monkeypatch.setattr(
        state_module,
        "state",
        {
            "enable_colors": False,
            "terminal_width": 40,
            "player": {"current_room": "lab", "name": "polaris"},
            "rooms": {"lab": {"name": "Lab D 2001"}},
            "game_state": {
                "phase": "EXPLORATION",
                "duration": {
                    "last_write": None,
                    "value": "00:05:00",
                    "pause": False,
                },
            },
        },
    )
    monkeypatch.setattr(display, "colorize", lambda text, color_code: text)
    out_mock = Mock()
    monkeypatch.setattr(display, "out", out_mock)
    monkeypatch.setattr(display, "draw_line", Mock())

    display.header("SAVED CHECKPOINTS")

    assert out_mock.call_args_list[1].args[0] == "SAVED CHECKPOINTS"
    assert out_mock.call_args_list[1].kwargs["end"] == " " * (
        40 - len("SAVED CHECKPOINTS") - len("polaris")
    )
    assert out_mock.call_args_list[2].args[0] == "POLARIS"
    assert out_mock.call_args_list[3].args[0] == "00:05:00"
