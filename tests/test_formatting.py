"""Tests for formatting utilities."""

from englog.utils.formatting import (
    calculate_duration_minutes,
    format_duration,
    get_current_time,
    get_today_date,
    parse_duration,
)


class TestFormatDuration:
    def test_minutes_only(self):
        assert format_duration(45) == "45m"

    def test_hours_and_minutes(self):
        assert format_duration(90) == "1h 30m"

    def test_zero_minutes(self):
        assert format_duration(0) == "0m"

    def test_exactly_one_hour(self):
        assert format_duration(60) == "1h 0m"

    def test_negative_becomes_zero(self):
        assert format_duration(-10) == "0m"


class TestParseDuration:
    def test_hours_and_minutes(self):
        assert parse_duration("1h 30m") == 90

    def test_minutes_only(self):
        assert parse_duration("45m") == 45

    def test_hours_only(self):
        assert parse_duration("2h") == 120

    def test_zero(self):
        assert parse_duration("0m") == 0


class TestCalculateDurationMinutes:
    def test_simple_difference(self):
        assert calculate_duration_minutes("09:00", "10:30") == 90

    def test_same_time(self):
        assert calculate_duration_minutes("09:00", "09:00") == 0

    def test_one_minute(self):
        assert calculate_duration_minutes("09:00", "09:01") == 1


class TestGetCurrentTime:
    def test_returns_string(self):
        result = get_current_time()
        assert isinstance(result, str)
        assert len(result) == 5  # HH:MM format
        assert ":" in result


class TestGetTodayDate:
    def test_returns_string(self):
        result = get_today_date()
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD format
        assert result.count("-") == 2
