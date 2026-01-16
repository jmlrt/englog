"""Environment variable handling for englog."""

import os
from pathlib import Path


def get_englog_dir() -> Path:
    """Get englog directory from $ENGLOG_DIR or default to ~/englog."""
    englog_dir = os.environ.get("ENGLOG_DIR")
    if englog_dir:
        return Path(englog_dir).expanduser()
    return Path.home() / "englog"


def get_editor() -> str:
    """Get editor from $EDITOR, raise error if not set."""
    editor = os.environ.get("EDITOR")
    if not editor:
        raise ValueError("EDITOR environment variable not set. Set it with: export EDITOR=vim")
    return editor
