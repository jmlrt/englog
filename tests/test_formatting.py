"""Tests for display helpers."""

import pytest

from englog.utils.formatting import format_duration


@pytest.mark.parametrize(
    ("minutes", "expected"),
    [(0, "0m"), (5, "5m"), (59, "59m"), (60, "1h"), (65, "1h 5m"), (150, "2h 30m"), (-3, "0m")],
)
def test_format_duration(minutes, expected):
    assert format_duration(minutes) == expected
