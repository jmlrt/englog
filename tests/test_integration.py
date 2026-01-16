"""Integration tests for critical end-to-end workflows.

These tests verify that CLI commands work together correctly and produce
the expected file output. Only test workflows that span multiple commands.
"""

from typer.testing import CliRunner

from englog.cli import app
from englog.core.file import read_daily_file

runner = CliRunner()


class TestTimerWorkflow:
    """Integration test for complete timer workflow."""

    def test_start_stop_persists_to_file(self, temp_englog_dir):
        """Verify timer start/stop creates correct markdown entry."""
        runner.invoke(app, ["time", "start", "Integration test @testing"])
        runner.invoke(app, ["time", "stop"])

        content = read_daily_file()
        assert "## Time" in content
        assert "Integration test" in content
        assert "@testing" in content
        assert "Duration:" in content


class TestTodoWorkflow:
    """Integration test for complete todo workflow."""

    def test_add_doing_done_persists_to_file(self, temp_englog_dir):
        """Verify todo state transitions create correct markdown."""
        runner.invoke(app, ["todo", "add", "Test task @work"])
        runner.invoke(app, ["todo", "doing", "1"])
        runner.invoke(app, ["todo", "done", "1"])

        content = read_daily_file()
        assert "## Todo" in content
        assert "### Done" in content
        assert "Test task" in content
        assert "@work" in content


class TestEntryWorkflow:
    """Integration test for entry commands."""

    def test_entries_persist_to_correct_sections(self, temp_englog_dir):
        """Verify til/note/scratch write to correct sections."""
        runner.invoke(app, ["til", "Learned something @learning"])
        runner.invoke(app, ["note", "Important info @reference"])
        runner.invoke(app, ["scratch", "Quick capture @debug"])

        content = read_daily_file()
        assert "## TIL" in content
        assert "Learned something" in content
        assert "## Notes" in content
        assert "Important info" in content
        assert "## Scratch" in content
        assert "Quick capture" in content
