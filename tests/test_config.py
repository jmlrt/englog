"""Tests for configuration handling."""

from pathlib import Path

import pytest

from englog.core.config import get_editor, get_englog_dir


class TestGetEnglogDir:
    def test_default_directory(self, monkeypatch):
        monkeypatch.delenv("ENGLOG_DIR", raising=False)
        result = get_englog_dir()
        assert result == Path.home() / "englog"

    def test_custom_directory(self, monkeypatch):
        monkeypatch.setenv("ENGLOG_DIR", "/custom/path")
        result = get_englog_dir()
        assert result == Path("/custom/path")

    def test_expands_tilde(self, monkeypatch):
        monkeypatch.setenv("ENGLOG_DIR", "~/my-englog")
        result = get_englog_dir()
        assert result == Path.home() / "my-englog"


class TestGetEditor:
    def test_returns_editor(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "vim")
        assert get_editor() == "vim"

    def test_raises_when_not_set(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with pytest.raises(ValueError, match="EDITOR environment variable not set"):
            get_editor()
