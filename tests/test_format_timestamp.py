"""Tests for ``src/utils/format_timestamp.py``."""

from src.utils.format_timestamp import format_timestamp


def test_format_timestamp_default():
    assert format_timestamp("2026-10-24T10:30:43.756Z") == "2026-10-24 10:30"


def test_format_timestamp_custom_format():
    assert format_timestamp("2026-10-24T10:30:43.756Z", "%H:%M") == "10:30"


def test_format_timestamp_empty_returns_empty():
    assert format_timestamp("") == ""
