"""Unit tests for utility CLI commands (init, status, edit, version).

Tests CLI-specific behavior only: exit codes, output messages.
"""

from typer.testing import CliRunner

from englog import __version__
from englog.cli import app

runner = CliRunner()


class TestInit:
    """Tests for englog init CLI behavior."""

    def test_already_initialized_message(self, temp_englog_dir):
        temp_englog_dir.mkdir(parents=True, exist_ok=True)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "already initialized" in result.output


class TestStatus:
    """Tests for englog status CLI behavior."""

    def test_shows_all_sections(self, temp_englog_dir):
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Active Timer:" in result.output
        assert "Time Today:" in result.output
        assert "Todos:" in result.output


class TestEdit:
    """Tests for englog edit CLI behavior."""

    def test_requires_editor_env_var(self, temp_englog_dir, no_editor):
        result = runner.invoke(app, ["edit"])
        assert result.exit_code == 1
        assert "EDITOR" in result.output


class TestVersion:
    """Tests for englog version CLI behavior."""

    def test_shows_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output
