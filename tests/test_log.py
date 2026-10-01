"""Tests for the daily time log (parsing, entries, start/stop)."""

from datetime import date

import pytest

from englog.core.log import (
    Entry,
    Line,
    build_entries,
    find_running,
    format_time,
    get_log_path,
    parse_lines,
    parse_time,
    start_entry,
    stop_entry,
)

DAY = date(2026, 10, 1)


class TestParseTime:
    @pytest.mark.parametrize(
        ("text", "minutes"),
        [("00:00", 0), ("09:05", 545), ("9:05", 545), ("23:59", 1439)],
    )
    def test_valid(self, text, minutes):
        assert parse_time(text) == minutes

    @pytest.mark.parametrize(
        "text",
        ["", "9", "24:00", "09:60", "09:5", "ab:cd", "09:30:00", "000:00", "0009:30", "٠٩:٣٠"],
    )
    def test_invalid(self, text):
        with pytest.raises(ValueError, match="Invalid time"):
            parse_time(text)

    def test_format_round_trip(self):
        assert format_time(parse_time("9:05")) == "09:05"


class TestParseLines:
    def test_parses_entries_and_stop(self):
        lines = parse_lines("09:00 day prep, check notifs\n09:30 stop\n", "f")
        assert lines == [Line(540, "day prep, check notifs"), Line(570, "stop")]

    def test_ignores_blank_lines(self):
        assert parse_lines("\n09:00 a\n\n", "f") == [Line(540, "a")]

    def test_equal_times_are_allowed(self):
        assert len(parse_lines("09:00 a\n09:00 b\n", "f")) == 2

    def test_missing_title(self):
        with pytest.raises(ValueError, match=r"f:1: missing title"):
            parse_lines("09:00\n", "f")

    def test_bad_time_reports_location(self):
        with pytest.raises(ValueError, match=r"f:2: Invalid time"):
            parse_lines("09:00 a\nlunch b\n", "f")

    def test_out_of_order(self):
        with pytest.raises(ValueError, match=r"f:2: .* earlier than the previous line"):
            parse_lines("10:00 a\n09:00 b\n", "f")

    def test_leading_stop(self):
        with pytest.raises(ValueError, match="stop without a running entry"):
            parse_lines("09:00 stop\n", "f")

    def test_double_stop(self):
        with pytest.raises(ValueError, match=r"f:3: stop without a running entry"):
            parse_lines("09:00 a\n10:00 stop\n11:00 stop\n", "f")


class TestBuildEntries:
    def test_entry_ends_at_next_line(self):
        entries = build_entries(parse_lines("09:00 a\n09:30 b\n10:00 stop\n", "f"))
        assert entries == [Entry(540, 570, "a"), Entry(570, 600, "b")]

    def test_stop_leaves_a_gap(self):
        entries = build_entries(parse_lines("09:00 a\n10:00 stop\n11:00 b\n", "f"))
        assert entries == [Entry(540, 600, "a"), Entry(660, None, "b")]

    def test_last_entry_is_running(self):
        entries = build_entries(parse_lines("09:00 a\n", "f"))
        assert find_running(entries) == Entry(540, None, "a")

    def test_nothing_running_after_stop(self):
        entries = build_entries(parse_lines("09:00 a\n10:00 stop\n", "f"))
        assert find_running(entries) is None

    def test_empty(self):
        assert build_entries([]) == []
        assert find_running([]) is None


class TestEntryMinutes:
    def test_finished(self):
        assert Entry(540, 600, "a").minutes(now=1000) == 60

    def test_running_uses_now(self):
        assert Entry(540, None, "a").minutes(now=600) == 60

    def test_never_negative(self):
        assert Entry(600, None, "a").minutes(now=540) == 0


class TestStartEntry:
    def test_creates_file(self, temp_englog_dir):
        assert start_entry(DAY, "day prep", at=540, now=540) is None
        assert (temp_englog_dir / "2026-10-01.txt").read_text() == "09:00 day prep\n"

    def test_ends_running_entry(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=540)
        ended = start_entry(DAY, "b", at=600, now=600)
        assert ended == Entry(540, 600, "a")
        assert get_log_path(DAY).read_text() == "09:00 a\n10:00 b\n"

    def test_after_stop_ends_nothing(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=540)
        stop_entry(DAY, at=600, now=600)
        assert start_entry(DAY, "b", at=660, now=660) is None

    def test_appends_after_hand_edit_without_trailing_newline(self, temp_englog_dir):
        get_log_path(DAY).write_text("09:00 a")
        start_entry(DAY, "b", at=600, now=600)
        assert get_log_path(DAY).read_text() == "09:00 a\n10:00 b\n"

    def test_past_start_time_allowed(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=700)
        assert get_log_path(DAY).read_text() == "09:00 a\n"

    def test_future_time_rejected(self, temp_englog_dir):
        with pytest.raises(ValueError, match="in the future"):
            start_entry(DAY, "a", at=700, now=600)

    def test_earlier_than_last_line_rejected(self, temp_englog_dir):
        start_entry(DAY, "a", at=600, now=600)
        with pytest.raises(ValueError, match="earlier than the last line"):
            start_entry(DAY, "b", at=540, now=700)
        assert get_log_path(DAY).read_text() == "10:00 a\n"

    @pytest.mark.parametrize("title", ["", "   ", "stop", " stop ", "a\nb", "a\rb"])
    def test_invalid_title_rejected(self, temp_englog_dir, title):
        with pytest.raises(ValueError):
            start_entry(DAY, title, at=540, now=540)
        assert not get_log_path(DAY).exists()

    def test_title_is_stripped_before_writing(self, temp_englog_dir):
        start_entry(DAY, "  day prep  ", at=540, now=540)
        assert get_log_path(DAY).read_text() == "09:00 day prep\n"

    def test_malformed_file_is_not_modified(self, temp_englog_dir):
        get_log_path(DAY).write_text("10:00 a\n09:00 b\n")
        with pytest.raises(ValueError, match="earlier than the previous line"):
            start_entry(DAY, "c", at=700, now=700)
        assert get_log_path(DAY).read_text() == "10:00 a\n09:00 b\n"


class TestStopEntry:
    def test_returns_ended_entry(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=540)
        assert stop_entry(DAY, at=600, now=600) == Entry(540, 600, "a")
        assert get_log_path(DAY).read_text() == "09:00 a\n10:00 stop\n"

    def test_no_running_entry(self, temp_englog_dir):
        with pytest.raises(ValueError, match="No running entry"):
            stop_entry(DAY, at=600, now=600)

    def test_already_stopped(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=540)
        stop_entry(DAY, at=600, now=600)
        with pytest.raises(ValueError, match="No running entry"):
            stop_entry(DAY, at=620, now=620)

    def test_future_time_rejected(self, temp_englog_dir):
        start_entry(DAY, "a", at=540, now=540)
        with pytest.raises(ValueError, match="in the future"):
            stop_entry(DAY, at=700, now=600)
