"""Main CLI entry point for englog."""

import subprocess

import typer

from englog import __version__
from englog.commands import note, scratch, til
from englog.core.config import get_editor, get_englog_dir
from englog.core.file import ensure_daily_file_exists

app = typer.Typer(
    help="Minimalist CLI for engineering workdays. Capture time tracking, todos, TILs, and notes as timestamped markdown.",
    no_args_is_help=True,
)


@app.command()
def init() -> None:
    """Initialize englog directory."""
    englog_dir = get_englog_dir()

    if englog_dir.exists():
        typer.echo(f"englog directory already initialized: {englog_dir}")
        return

    try:
        englog_dir.mkdir(parents=True, exist_ok=True)
        typer.echo(f"Initialized englog directory: {englog_dir}")
    except OSError as e:
        typer.echo(f"Cannot create directory: {englog_dir} ({e})", err=True)
        raise typer.Exit(1)


@app.command()
def edit() -> None:
    """Open today's file in $EDITOR."""
    try:
        editor = get_editor()
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    file_path = ensure_daily_file_exists()
    subprocess.run([editor, str(file_path)])


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"englog {__version__}")


# Register simple commands
app.command(name="til")(til.til_command)
app.command(name="note")(note.note_command)
app.command(name="scratch")(scratch.scratch_command)


if __name__ == "__main__":
    app()
