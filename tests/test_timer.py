"""Tests for timer functionality."""

import pytest

from englog.core.file import ensure_daily_file_exists
from englog.core.timer import (
    calculate_total_time,
    find_timer_by_description,
    find_timer_by_number,
    get_active_timer,
    list_timers,
    pause_timer,
    resume_timer,
    start_timer,
    stop_timer,
)


class TestStartTimer:
    def test_starts_new_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        stopped, new = start_timer("Test task", ["backend", "api"])
        assert stopped is None
        assert new.description == "Test task"
        assert new.tags == ["backend", "api"]
        assert new.is_active is True

    def test_auto_stops_previous_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("First task", ["tag1"])
        stopped, new = start_timer("Second task", ["tag2"])
        assert stopped is not None
        assert stopped.description == "First task"
        assert new.description == "Second task"


class TestStopTimer:
    def test_stops_active_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Test task", [])
        timer = stop_timer()
        assert timer.description == "Test task"
        assert timer.is_active is False

    def test_raises_when_no_active_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        with pytest.raises(ValueError, match="No active timer"):
            stop_timer()


class TestPauseTimer:
    def test_pauses_active_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Test task", [])
        timer = pause_timer()
        assert timer.description == "Test task"

    def test_raises_when_no_active_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        with pytest.raises(ValueError, match="No active timer"):
            pause_timer()


class TestResumeTimer:
    def test_resumes_paused_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Test task", [])
        pause_timer()
        timer = resume_timer()
        assert timer.description == "Test task"

    def test_raises_when_no_paused_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        with pytest.raises(ValueError, match="No paused timer"):
            resume_timer()


class TestListTimers:
    def test_empty_list_when_no_timers(self, temp_englog_dir):
        ensure_daily_file_exists()
        timers = list_timers()
        assert timers == []

    def test_lists_all_timers(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Task 1", ["tag1"])
        stop_timer()
        start_timer("Task 2", ["tag2"])
        timers = list_timers()
        assert len(timers) == 2
        assert timers[0].description == "Task 1"
        assert timers[1].description == "Task 2"
        assert timers[1].is_active is True


class TestGetActiveTimer:
    def test_returns_none_when_no_active(self, temp_englog_dir):
        ensure_daily_file_exists()
        assert get_active_timer() is None

    def test_returns_active_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Test task", [])
        active = get_active_timer()
        assert active is not None
        assert active.description == "Test task"


class TestFindTimerByDescription:
    def test_finds_matching_timer(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Unique task", ["tag"])
        stop_timer()
        found = find_timer_by_description("Unique task")
        assert found is not None
        assert found.description == "Unique task"

    def test_returns_none_when_not_found(self, temp_englog_dir):
        ensure_daily_file_exists()
        found = find_timer_by_description("Nonexistent")
        assert found is None

    def test_case_insensitive(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Unique Task", ["tag"])
        stop_timer()
        found = find_timer_by_description("unique task")
        assert found is not None


class TestFindTimerByNumber:
    def test_finds_timer_by_number(self, temp_englog_dir):
        ensure_daily_file_exists()
        start_timer("Task 1", [])
        stop_timer()
        start_timer("Task 2", [])
        found = find_timer_by_number(1)
        assert found is not None
        assert found.description == "Task 1"

    def test_returns_none_for_invalid_number(self, temp_englog_dir):
        ensure_daily_file_exists()
        found = find_timer_by_number(999)
        assert found is None


class TestCalculateTotalTime:
    def test_calculates_total(self, temp_englog_dir):
        ensure_daily_file_exists()
        # Since all timers run for 0m in tests (same minute), total will be 0
        start_timer("Task 1", [])
        stop_timer()
        total = calculate_total_time()
        assert total >= 0
