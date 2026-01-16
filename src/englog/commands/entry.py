"""Shared entry command logic for TIL, Notes, and Scratch."""

import subprocess
import tempfile

import typer

from englog.core.config import get_editor
from englog.core.file import append_to_section
from englog.core.tags import extract_tags_from_text, format_tags
from englog.utils.formatting import get_current_time


def create_entry_command(section: str, name: str):
    """Factory to create entry commands for TIL, Notes, and Scratch."""

    def command(
        content: str | None = typer.Argument(None, help=f"{name} content with @tags"),
        edit: bool = typer.Option(False, "--edit", "-e", help="Open editor for multi-line input"),
        tags: list[str] | None = typer.Argument(None, help="Tags when using --edit"),
    ) -> None:
        if edit:
            _add_with_editor(section, name, tags or [])
        elif content:
            _add_inline(section, name, content)
        else:
            typer.echo("Error: Provide content or use --edit flag", err=True)
            raise typer.Exit(1)

    return command


def _add_inline(section: str, name: str, content: str) -> None:
    """Add entry from inline content."""
    text, tags = extract_tags_from_text(content)

    if not text:
        typer.echo("Warning: Empty content, entry not created", err=True)
        return

    timestamp = get_current_time()
    tags_str = format_tags(tags)

    entry = f"### {timestamp} | {tags_str}\n{text}"
    append_to_section(section, entry)

    preview = f"{text[:50]}..." if len(text) > 50 else text
    typer.echo(f"{name} added: {preview}")


def _add_with_editor(section: str, name: str, cli_tags: list[str]) -> None:
    """Add entry using editor."""
    try:
        editor = get_editor()
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    tags = [tag.lstrip("@") for tag in cli_tags]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        temp_path = f.name

    subprocess.run([editor, temp_path])

    with open(temp_path) as f:
        content = f.read().strip()

    if not content:
        typer.echo("Warning: Empty content, entry not created", err=True)
        return

    timestamp = get_current_time()
    tags_str = format_tags(tags)

    entry = f"### {timestamp} | {tags_str}\n{content}"
    append_to_section(section, entry)

    preview = f"{content[:50]}..." if len(content) > 50 else content
    typer.echo(f"{name} added: {preview}")
