"""Tests for ``src/utils/username_generator.py``."""

from contextlib import contextmanager
from unittest.mock import Mock

import src.utils.username_generator as generator


def _fake_connection(fetchone_results):
    """Build a fake ``connection()`` context manager and its cursor."""
    cursor = Mock()
    cursor.fetchone.side_effect = fetchone_results
    conn = Mock()
    conn.execute.return_value = cursor

    @contextmanager
    def connection():
        yield conn

    return connection, conn, cursor


def test_generate_random_username_returns_first_free(monkeypatch):
    connection, conn, cursor = _fake_connection([None])
    monkeypatch.setattr(generator, "connection", connection)

    fake_random = Mock()
    fake_random.choice.side_effect = lambda seq: seq[0]
    fake_random.randint.return_value = 123
    monkeypatch.setattr(generator, "random", fake_random)

    assert generator.generate_random_username() == "Operator_Aegis_123"
    conn.execute.assert_called_once_with(
        "SELECT 1 FROM users WHERE name = ?", ("Operator_Aegis_123",)
    )
    assert cursor.fetchone.call_count == 1


def test_generate_random_username_retries_on_collision(monkeypatch):
    connection, conn, cursor = _fake_connection([object(), None])
    monkeypatch.setattr(generator, "connection", connection)

    fake_random = Mock()
    fake_random.choice.side_effect = lambda seq: seq[0]
    fake_random.randint.side_effect = [111, 222]
    monkeypatch.setattr(generator, "random", fake_random)

    assert generator.generate_random_username() == "Operator_Aegis_222"
    assert conn.execute.call_count == 2
    assert cursor.fetchone.call_count == 2
