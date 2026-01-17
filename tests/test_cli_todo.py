"""Unit tests for todo CLI commands.

Tests CLI-specific behavior only: exit codes, output messages, argument handling.
Core todo logic is tested in test_todo.py.
"""

from typer.testing import CliRunner

from englog.cli import app

runner = CliRunner()


class TestTodoAdd:
    """Tests for englog todo add CLI behavior."""

    def test_success_output(self, temp_englog_dir):
        result = runner.invoke(app, ["todo", "add", "Test task"])
        assert result.exit_code == 0
        assert "Added:" in result.output

    def test_empty_description_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["todo", "add", "@tag1"])
        assert result.exit_code == 1
        assert "empty" in result.output.lower()


class TestTodoDoing:
    """Tests for englog todo doing CLI behavior."""

    def test_not_found_by_number_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["todo", "doing", "99"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestTodoDone:
    """Tests for englog todo done CLI behavior."""

    def test_not_found_by_number_exits_with_error(self, temp_englog_dir):
        result = runner.invoke(app, ["todo", "done", "99"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestTodoList:
    """Tests for englog todo list CLI behavior."""

    def test_empty_list_message(self, temp_englog_dir):
        result = runner.invoke(app, ["todo", "list"])
        assert result.exit_code == 0
        assert "No todos today" in result.output
