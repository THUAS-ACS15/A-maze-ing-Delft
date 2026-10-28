"""Tests for ``src.utils.parse_time``."""

from datetime import timedelta

import pytest

from src.utils.parse_time import parse_time_str


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("00:00:00", timedelta(0), id="zero"),
        pytest.param("0:06:39", timedelta(minutes=6, seconds=39), id="short"),
        pytest.param(
            "1 day, 1:00:00",
            timedelta(days=1, hours=1),
            id="one-day",
        ),
        pytest.param(
            "2 days, 2:26:59",
            timedelta(days=2, hours=2, minutes=26, seconds=59),
            id="multiple-days",
        ),
    ],
)
def test_parse_time_str(value, expected):
    assert parse_time_str(value) == expected
