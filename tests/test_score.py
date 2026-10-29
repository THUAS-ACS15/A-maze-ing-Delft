"""Tests for ``src/utils/score.py``."""

from datetime import timedelta

from src.utils.score import calculate_score


def test_zero_time_scores_base():
    assert calculate_score(timedelta(0), timedelta(0)) == 1000


def test_exploration_time_reduces_score():
    assert calculate_score(timedelta(minutes=10), timedelta(0)) == 880


def test_assembly_time_reduces_score():
    assert calculate_score(timedelta(0), timedelta(minutes=5)) == 980


def test_exploration_and_assembly_are_weighted_together():
    assert calculate_score(timedelta(minutes=10), timedelta(minutes=5)) == 860


def test_score_never_drops_below_zero():
    assert calculate_score(timedelta(hours=10), timedelta(hours=10)) == 0
