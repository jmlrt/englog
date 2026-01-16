"""Shared test fixtures for englog."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_englog_dir(monkeypatch):
    """Create a temporary englog directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("ENGLOG_DIR", tmpdir)
        yield Path(tmpdir)


@pytest.fixture
def mock_editor(monkeypatch):
    """Mock the EDITOR environment variable."""
    monkeypatch.setenv("EDITOR", "cat")  # cat is a no-op for testing
    yield "cat"


@pytest.fixture
def no_editor(monkeypatch):
    """Remove EDITOR environment variable."""
    monkeypatch.delenv("EDITOR", raising=False)
    yield
