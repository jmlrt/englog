"""Unit tests for entry CLI commands (til, note, scratch).

Tests CLI-specific behavior only: exit codes, output messages, argument handling.
Core file operations are tested in test_file.py.
"""

from typer.testing import CliRunner

from englog.cli import app

runner = CliRunner()


class TestTil:
    """Tests for englog til CLI behavior."""

    def test_success_output(self, temp_englog_dir):
        result = runner.invoke(app, ["til", "Learned something new"])
        assert result.exit_code == 0
        assert "TIL added:" in result.output

    def test_empty_content_warning(self, temp_englog_dir):
        result = runner.invoke(app, ["til", "@tag1"])
        assert result.exit_code == 0
        assert "Empty content" in result.output

    def test_no_args_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["til"])
        assert result.exit_code == 1
        assert "Provide content or use --edit" in result.output


class TestNote:
    """Tests for englog note CLI behavior."""

    def test_success_output(self, temp_englog_dir):
        result = runner.invoke(app, ["note", "Important note"])
        assert result.exit_code == 0
        assert "Note added:" in result.output

    def test_no_args_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["note"])
        assert result.exit_code == 1


class TestScratch:
    """Tests for englog scratch CLI behavior."""

    def test_success_output(self, temp_englog_dir):
        result = runner.invoke(app, ["scratch", "Quick capture"])
        assert result.exit_code == 0
        assert "Scratch added:" in result.output

    def test_no_args_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["scratch"])
        assert result.exit_code == 1
