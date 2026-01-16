"""Tests for file operations."""

from datetime import date

from englog.core.file import (
    append_to_section,
    ensure_daily_file_exists,
    get_daily_file_path,
    get_section_content,
    read_daily_file,
    replace_section_content,
    write_daily_file,
)


class TestGetDailyFilePath:
    def test_returns_path_for_today(self, temp_englog_dir):
        from englog.utils.formatting import get_today_date

        result = get_daily_file_path()
        expected = temp_englog_dir / f"{get_today_date()}.md"
        assert result == expected

    def test_returns_path_for_specific_date(self, temp_englog_dir):
        result = get_daily_file_path(date(2025, 1, 15))
        expected = temp_englog_dir / "2025-01-15.md"
        assert result == expected


class TestEnsureDailyFileExists:
    def test_creates_file_if_not_exists(self, temp_englog_dir):
        file_path = ensure_daily_file_exists()
        assert file_path.exists()
        content = file_path.read_text()
        assert content.startswith("#")

    def test_does_not_overwrite_existing(self, temp_englog_dir):
        file_path = ensure_daily_file_exists()
        file_path.write_text("# Existing content\n\nSome data")
        ensure_daily_file_exists()
        content = file_path.read_text()
        assert "Some data" in content


class TestReadWriteDailyFile:
    def test_read_empty_when_no_file(self, temp_englog_dir):
        result = read_daily_file()
        assert result == ""

    def test_write_and_read(self, temp_englog_dir):
        write_daily_file("# Test\n\nContent")
        result = read_daily_file()
        assert "Content" in result


class TestAppendToSection:
    def test_creates_section_if_not_exists(self, temp_englog_dir):
        ensure_daily_file_exists()
        append_to_section("Notes", "### 10:00 | @test\nNote content")
        content = read_daily_file()
        assert "## Notes" in content
        assert "Note content" in content

    def test_appends_to_existing_section(self, temp_englog_dir):
        ensure_daily_file_exists()
        append_to_section("Notes", "### 10:00 | @test\nFirst note")
        append_to_section("Notes", "### 11:00 | @test\nSecond note")
        content = read_daily_file()
        assert "First note" in content
        assert "Second note" in content

    def test_maintains_section_order(self, temp_englog_dir):
        ensure_daily_file_exists()
        append_to_section("Scratch", "Scratch content")
        append_to_section("Time", "Time content")
        content = read_daily_file()
        time_pos = content.find("## Time")
        scratch_pos = content.find("## Scratch")
        assert time_pos < scratch_pos


class TestGetSectionContent:
    def test_returns_empty_for_missing_section(self, temp_englog_dir):
        ensure_daily_file_exists()
        result = get_section_content("Notes")
        assert result == ""

    def test_returns_section_content(self, temp_englog_dir):
        ensure_daily_file_exists()
        append_to_section("Notes", "### 10:00 | @test\nNote content")
        result = get_section_content("Notes")
        assert "Note content" in result


class TestReplaceSectionContent:
    def test_replaces_content(self, temp_englog_dir):
        ensure_daily_file_exists()
        append_to_section("Notes", "Old content")
        replace_section_content("Notes", "New content")
        result = get_section_content("Notes")
        assert "New content" in result
        assert "Old content" not in result

    def test_creates_section_if_not_exists(self, temp_englog_dir):
        ensure_daily_file_exists()
        replace_section_content("Notes", "New content")
        result = get_section_content("Notes")
        assert "New content" in result
