"""Main CLI entry point for englog."""

import subprocess

import typer

from englog import __version__
from englog.commands import note, scratch, til, time, todo
from englog.core.config import get_editor, get_englog_dir
from englog.core.file import ensure_daily_file_exists
from englog.core.tags import format_tags
from englog.core.timer import calculate_total_time, get_active_timer
from englog.core.todo import get_todo_counts
from englog.utils.formatting import (
    calculate_duration_minutes,
    format_duration,
    get_current_time,
    pluralize,
)

app = typer.Typer(
    help="Minimalist CLI for engineering workdays. Capture time tracking, todos, TILs, and notes as timestamped markdown.",
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(time.app, name="time", help="Time tracking commands")
app.add_typer(todo.app, name="todo", help="Todo management commands")


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
def status() -> None:
    """Show overview: active timer, todo counts, time today."""
    typer.echo("")
    typer.echo("Active Timer:")
    active = get_active_timer()
    if active:
        tags_str = format_tags(active.tags)
        duration = calculate_duration_minutes(active.start_time, get_current_time())
        typer.echo(f"  {active.description} {tags_str}")
        typer.echo(f"  Started: {active.start_time} (running {format_duration(duration)})")
    else:
        typer.echo("  None")

    typer.echo("")
    typer.echo(f"Time Today: {format_duration(calculate_total_time())}")

    typer.echo("")
    typer.echo("Todos:")
    counts = get_todo_counts()
    if all(c == 0 for c in counts.values()):
        typer.echo("  No todos today")
    else:
        for section in ("Todo", "Doing", "Done"):
            typer.echo(f"  {section}: {counts[section]} {pluralize(counts[section], 'task')}")


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
