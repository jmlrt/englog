"""Tests for the CLI: arguments, output, exit codes."""

from datetime import date

import pytest
from typer.testing import CliRunner

from englog import __version__
from englog.cli import app

runner = CliRunner()
DAY = date(2026, 10, 1)
NOW = 10 * 60  # 10:00


@pytest.fixture(autouse=True)
def fixed_now(monkeypatch):
    monkeypatch.setattr("englog.cli._now", lambda: (DAY, NOW))


def read_log(directory):
    return (directory / "2026-10-01.txt").read_text()


class TestStart:
    def test_unquoted_multi_word_title(self, temp_englog_dir):
        result = runner.invoke(app, ["start", "day", "prep,", "check", "notifs"])
        assert result.exit_code == 0
        assert "Started: day prep, check notifs" in result.output
        assert read_log(temp_englog_dir) == "10:00 day prep, check notifs\n"

    def test_at_before_title(self, temp_englog_dir):
        result = runner.invoke(app, ["start", "--at", "9:30", "1/1", "alice"])
        assert result.exit_code == 0
        assert read_log(temp_englog_dir) == "09:30 1/1 alice\n"

    def test_at_after_title_is_part_of_the_title(self, temp_englog_dir):
        result = runner.invoke(app, ["start", "review", "--at", "09:00"])
        assert result.exit_code == 0
        assert read_log(temp_englog_dir) == "10:00 review --at 09:00\n"

    def test_reports_ended_entry(self, temp_englog_dir):
        runner.invoke(app, ["start", "--at", "09:00", "first"])
        result = runner.invoke(app, ["start", "second"])
        assert "Stopped: first (1h), Started: second" in result.output

    def test_invalid_at(self, temp_englog_dir):
        result = runner.invoke(app, ["start", "--at", "25:00", "x"])
        assert result.exit_code == 1
        assert "Invalid time" in result.output

    def test_future_at(self, temp_englog_dir):
        result = runner.invoke(app, ["start", "--at", "11:00", "x"])
        assert result.exit_code == 1
        assert "in the future" in result.output

    @pytest.mark.parametrize("title", ["", "   "])
    def test_empty_title(self, temp_englog_dir, title):
        result = runner.invoke(app, ["start", title])
        assert result.exit_code == 1
        assert "empty" in result.output
        assert not (temp_englog_dir / "2026-10-01.txt").exists()

    @pytest.mark.parametrize("title", ["stop", " stop "])
    def test_reserved_title(self, temp_englog_dir, title):
        result = runner.invoke(app, ["start", title])
        assert result.exit_code == 1
        assert "reserved" in result.output

    def test_missing_title(self, temp_englog_dir):
        assert runner.invoke(app, ["start"]).exit_code != 0


class TestStop:
    def test_stops_running_entry(self, temp_englog_dir):
        runner.invoke(app, ["start", "--at", "09:00", "work"])
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0
        assert "Stopped: work (1h)" in result.output
        assert read_log(temp_englog_dir) == "09:00 work\n10:00 stop\n"

    def test_at(self, temp_englog_dir):
        runner.invoke(app, ["start", "--at", "09:00", "work"])
        result = runner.invoke(app, ["stop", "--at", "09:45"])
        assert "Stopped: work (45m)" in result.output

    def test_nothing_running(self, temp_englog_dir):
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 1
        assert "No running entry" in result.output


class TestList:
    def test_no_entries(self, temp_englog_dir):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No entries today" in result.output

    def test_entries_and_total(self, temp_englog_dir):
        (temp_englog_dir / "2026-10-01.txt").write_text(
            "08:00 day prep\n08:30 review\n09:00 stop\n09:30 sync\n"
        )
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "08:00-08:30 day prep (30m)" in result.output
        assert "08:30-09:00 review (30m)" in result.output
        assert "09:30-now sync (30m)" in result.output
        assert "Total: 1h 30m" in result.output

    def test_malformed_file(self, temp_englog_dir):
        (temp_englog_dir / "2026-10-01.txt").write_text("10:00 a\n09:00 b\n")
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 1
        assert "2026-10-01.txt:2" in result.output


class TestStatus:
    def test_nothing_running(self, temp_englog_dir):
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Running: none" in result.output
        assert "Time Today: 0m" in result.output

    def test_running(self, temp_englog_dir):
        (temp_englog_dir / "2026-10-01.txt").write_text("08:00 a\n09:00 b\n")
        result = runner.invoke(app, ["status"])
        assert "Running: b (since 09:00, 1h)" in result.output
        assert "Time Today: 2h" in result.output

    def test_stopped(self, temp_englog_dir):
        (temp_englog_dir / "2026-10-01.txt").write_text("08:00 a\n08:45 stop\n")
        result = runner.invoke(app, ["status"])
        assert "Running: none" in result.output
        assert "Time Today: 45m" in result.output


class TestEdit:
    def test_creates_and_opens_file(self, temp_englog_dir, mock_editor):
        result = runner.invoke(app, ["edit"])
        assert result.exit_code == 0
        assert (temp_englog_dir / "2026-10-01.txt").exists()

    def test_requires_editor(self, temp_englog_dir, no_editor):
        result = runner.invoke(app, ["edit"])
        assert result.exit_code == 1
        assert "EDITOR" in result.output


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output
