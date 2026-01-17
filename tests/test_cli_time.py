"""Unit tests for time CLI commands.

Tests CLI-specific behavior only: exit codes, output messages, argument handling.
Core timer logic is tested in test_timer.py.
"""

from typer.testing import CliRunner

from englog.cli import app

runner = CliRunner()


class TestTimeStart:
    """Tests for englog time start CLI behavior."""

    def test_success_output(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "start", "Test task"])
        assert result.exit_code == 0
        assert "Started:" in result.output

    def test_empty_description_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "start", "@tag1"])
        assert result.exit_code == 1
        assert "empty" in result.output.lower()

    def test_invalid_number_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "start", "99"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestTimeStop:
    """Tests for englog time stop CLI behavior."""

    def test_no_active_timer_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "stop"])
        assert result.exit_code == 1
        assert "No active timer" in result.output


class TestTimePauseResume:
    """Tests for englog time pause/resume CLI behavior."""

    def test_pause_no_timer_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "pause"])
        assert result.exit_code == 1

    def test_resume_no_timer_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "resume"])
        assert result.exit_code == 1


class TestTimeList:
    """Tests for englog time list CLI behavior."""

    def test_empty_list_message(self, temp_englog_dir):
        result = runner.invoke(app, ["time", "list"])
        assert result.exit_code == 0
        assert "No timers today" in result.output
