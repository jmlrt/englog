"""Note command for englog."""

from englog.commands.entry import create_entry_command

note_command = create_entry_command("Notes", "Note")
note_command.__doc__ = "Capture a quick note."
