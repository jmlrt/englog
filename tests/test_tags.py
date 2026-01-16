"""Tests for tag parsing and formatting."""

from englog.core.tags import extract_tags_from_text, format_tags, parse_tags


class TestParseTags:
    def test_single_tag(self):
        assert parse_tags("hello @world") == ["world"]

    def test_multiple_tags(self):
        assert parse_tags("task @python @backend @api") == ["python", "backend", "api"]

    def test_no_tags(self):
        assert parse_tags("no tags here") == []

    def test_tag_with_hyphen(self):
        assert parse_tags("@my-project") == ["my-project"]

    def test_tag_with_underscore(self):
        assert parse_tags("@my_project") == ["my_project"]

    def test_tag_with_numbers(self):
        assert parse_tags("@v2 @project123") == ["v2", "project123"]


class TestExtractTagsFromText:
    def test_extract_tags(self):
        content, tags = extract_tags_from_text("Fix bug @backend @urgent")
        assert content == "Fix bug"
        assert tags == ["backend", "urgent"]

    def test_no_tags(self):
        content, tags = extract_tags_from_text("Fix bug")
        assert content == "Fix bug"
        assert tags == []

    def test_only_tags(self):
        content, tags = extract_tags_from_text("@backend @urgent")
        assert content == ""
        assert tags == ["backend", "urgent"]

    def test_tags_in_middle(self):
        content, tags = extract_tags_from_text("Fix @backend bug @urgent now")
        assert content == "Fix bug now"
        assert tags == ["backend", "urgent"]


class TestFormatTags:
    def test_format_tags(self):
        assert format_tags(["python", "backend"]) == "@python @backend"

    def test_empty_tags(self):
        assert format_tags([]) == ""

    def test_single_tag(self):
        assert format_tags(["python"]) == "@python"
