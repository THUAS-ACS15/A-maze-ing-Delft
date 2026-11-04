from datetime import timedelta

import pytest

from src.utils.duration import calculate_duration


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ("2026-01-01T10:00:00", "2026-01-01T11:00:00", timedelta(hours=1)),
        ("2026-01-01T10:00:00", "2026-01-01T10:30:00", timedelta(minutes=30)),
        ("2026-01-01T10:00:00", "2026-01-01T10:00:45", timedelta(seconds=45)),
        ("2026-01-01T00:00:00", "2026-01-02T00:00:00", timedelta(days=1)),
        ("2026-01-01T10:00:00", "2026-01-01T10:00:00", timedelta(0)),
        ("2026-01-01T11:00:00", "2026-01-01T10:00:00", timedelta(hours=-1)),
    ],
)
def test_calculate_duration(start, end, expected):
    assert calculate_duration(start, end) == expected


@pytest.mark.parametrize(
    "start, end, expected",
    [
        # microseconds are stripped, so this is a zero-length duration
        ("2026-01-01T10:00:00", "2026-01-01T10:00:00.123456", timedelta(0)),
        ("2026-01-01T10:00:00.500000", "2026-01-01T10:00:05.750000", timedelta(seconds=5)),
    ],
)
def test_calculate_duration_strips_microseconds(start, end, expected):
    assert calculate_duration(start, end) == expected


@pytest.mark.parametrize(
    "start, end",
    [
        ("", "2026-01-01T10:00:00"),
        ("2026-01-01T10:00:00", ""),
        ("not-a-timestamp", "2026-01-01T10:00:00"),
        ("2026-01-01T10:00:00", "garbage"),
    ],
)
def test_calculate_duration_invalid_raises(start, end):
    with pytest.raises(ValueError):
        calculate_duration(start, end)
