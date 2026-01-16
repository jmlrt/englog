"""Scratch command for englog."""

from englog.commands.entry import create_entry_command

scratch_command = create_entry_command("Scratch", "Scratch")
scratch_command.__doc__ = "Capture temporary/ephemeral content."
