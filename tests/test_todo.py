"""Tests for todo functionality."""

from englog.core.file import ensure_daily_file_exists
from englog.core.todo import (
    add_todo,
    find_todo_by_description,
    find_todo_by_number,
    get_todo_counts,
    list_todos_with_numbers,
    move_todo,
)


class TestAddTodo:
    def test_adds_todo_to_default_section(self, temp_englog_dir):
        ensure_daily_file_exists()
        todo = add_todo("Test task", ["backend"])
        assert todo.description == "Test task"
        assert todo.tags == ["backend"]
        assert todo.section == "Todo"

    def test_adds_todo_to_specified_section(self, temp_englog_dir):
        ensure_daily_file_exists()
        todo = add_todo("Test task", [], "Doing")
        assert todo.section == "Doing"


class TestFindTodoByDescription:
    def test_finds_matching_todo(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Unique task", ["tag"])
        found = find_todo_by_description("Unique task")
        assert found is not None
        assert found.description == "Unique task"

    def test_returns_none_when_not_found(self, temp_englog_dir):
        ensure_daily_file_exists()
        found = find_todo_by_description("Nonexistent")
        assert found is None

    def test_case_insensitive(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Unique Task", ["tag"])
        found = find_todo_by_description("unique task")
        assert found is not None


class TestFindTodoByNumber:
    def test_finds_todo_by_number(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Task 1", [])
        add_todo("Task 2", [])
        found = find_todo_by_number(1)
        assert found is not None
        assert found.description == "Task 1"

    def test_returns_none_for_invalid_number(self, temp_englog_dir):
        ensure_daily_file_exists()
        found = find_todo_by_number(999)
        assert found is None

    def test_does_not_find_done_items(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Task 1", [], "Done")
        found = find_todo_by_number(1)
        assert found is None


class TestMoveTodo:
    def test_moves_todo_to_doing(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Test task", ["tag"])
        original = find_todo_by_description("Test task")
        moved = move_todo(original, "Doing")
        assert moved.section == "Doing"

    def test_moves_todo_to_done(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Test task", ["tag"])
        original = find_todo_by_description("Test task")
        moved = move_todo(original, "Done")
        assert moved.section == "Done"


class TestListTodosWithNumbers:
    def test_empty_list_when_no_todos(self, temp_englog_dir):
        ensure_daily_file_exists()
        todos = list_todos_with_numbers()
        assert todos == []

    def test_numbers_assigned_to_todo_and_doing(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Task 1", [], "Todo")
        add_todo("Task 2", [], "Doing")
        add_todo("Task 3", [], "Done")
        todos = list_todos_with_numbers()

        todo_items = [t for t in todos if t.section == "Todo"]
        doing_items = [t for t in todos if t.section == "Doing"]
        done_items = [t for t in todos if t.section == "Done"]

        assert len(todo_items) == 1
        assert todo_items[0].number == 1
        assert len(doing_items) == 1
        assert doing_items[0].number == 2
        assert len(done_items) == 1
        assert done_items[0].number is None


class TestGetTodoCounts:
    def test_all_zero_when_empty(self, temp_englog_dir):
        ensure_daily_file_exists()
        counts = get_todo_counts()
        assert counts == {"Todo": 0, "Doing": 0, "Done": 0}

    def test_counts_correctly(self, temp_englog_dir):
        ensure_daily_file_exists()
        add_todo("Task 1", [], "Todo")
        add_todo("Task 2", [], "Todo")
        add_todo("Task 3", [], "Doing")
        add_todo("Task 4", [], "Done")
        counts = get_todo_counts()
        assert counts == {"Todo": 2, "Doing": 1, "Done": 1}
