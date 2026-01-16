"""TIL (Today I Learned) command for englog."""

from englog.commands.entry import create_entry_command

til_command = create_entry_command("TIL", "TIL")
til_command.__doc__ = "Capture a Today I Learned entry."
