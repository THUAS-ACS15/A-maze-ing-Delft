import pytest

from teachers_room_2 import inspect

@pytest.mark.parametrize(
    "target, expected",
    [
        ("whiteboard", None),
        ("  USER@Example.COM  ", None),
        ('"quoted@email.com"', None),
        ("'single@email.com'", None),
        ("a.b@c.d.e", None),
        ("user+tag@mail.example.co", None),
    ],
)
def test_valid_inspect(target: str, expected: str) -> None:
    assert inspect(target) == expected

@pytest.mark.parametrize(
    "target, expected",
    [
        ("whiteboard", None),
        ("  USER@Example.COM  ", None),
        ('"quoted@email.com"', None),
        ("'single@email.com'", None),
        ("a.b@c.d.e", None),
        ("user+tag@mail.example.co", None),
    ],
)
def test_invalid_inspect(target: str, expected: str) -> None:
    assert inspect(target) == expected