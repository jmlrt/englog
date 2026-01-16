"""Integration tests for critical end-to-end workflows.

These tests verify that CLI commands work together correctly and produce
the expected file output. Only test workflows that span multiple commands.
"""

from typer.testing import CliRunner

from englog.cli import app
from englog.core.file import read_daily_file

runner = CliRunner()


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
