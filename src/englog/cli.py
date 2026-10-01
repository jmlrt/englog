"""Main CLI entry point for englog."""

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime

import typer

from englog import __version__
from englog.core.config import get_editor
from englog.core.log import (
    build_entries,
    find_running,
    format_time,
    get_log_path,
    parse_time,
    read_lines,
    start_entry,
    stop_entry,
)
from englog.utils.formatting import format_duration

app = typer.Typer(
    help="Minimalist time log for engineering workdays.",
    no_args_is_help=True,
)


def _now() -> tuple[date, int]:
    now = datetime.now()
    return now.date(), now.hour * 60 + now.minute


@contextmanager
def _exit_on_error() -> Iterator[None]:
    try:
        yield
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1)


@app.command(context_settings={"allow_interspersed_args": False})
def start(
    title: list[str] = typer.Argument(..., help="Entry title, no quotes needed"),
    at: str | None = typer.Option(None, "--at", help="Start time HH:MM (default: now)"),
) -> None:
    """Start an entry, ending the running one: start [--at HH:MM] TITLE..."""
    day, now = _now()
    text = " ".join(title)
    with _exit_on_error():
        stopped = start_entry(day, text, parse_time(at) if at else now, now)
    if stopped:
        typer.echo(
            f"Stopped: {stopped.title} ({format_duration(stopped.minutes(now))}), Started: {text}"
        )
    else:
        typer.echo(f"Started: {text}")


@app.command()
def stop(
    at: str | None = typer.Option(None, "--at", help="Stop time HH:MM (default: now)"),
) -> None:
    """Stop the running entry."""
    day, now = _now()
    with _exit_on_error():
        stopped = stop_entry(day, parse_time(at) if at else now, now)
    typer.echo(f"Stopped: {stopped.title} ({format_duration(stopped.minutes(now))})")


@app.command(name="list")
def list_cmd() -> None:
    """List today's entries with durations."""
    day, now = _now()
    with _exit_on_error():
        entries = build_entries(read_lines(day))
    if not entries:
        typer.echo("No entries today")
        return
    for entry in entries:
        end = "now" if entry.end is None else format_time(entry.end)
        typer.echo(
            f"{format_time(entry.start)}-{end} {entry.title} "
            f"({format_duration(entry.minutes(now))})"
        )
    typer.echo("")
    typer.echo(f"Total: {format_duration(sum(entry.minutes(now) for entry in entries))}")


@app.command()
def status() -> None:
    """Show the running entry and today's total."""
    day, now = _now()
    with _exit_on_error():
        entries = build_entries(read_lines(day))
    running = find_running(entries)
    if running:
        typer.echo(
            f"Running: {running.title} "
            f"(since {format_time(running.start)}, {format_duration(running.minutes(now))})"
        )
    else:
        typer.echo("Running: none")
    typer.echo(f"Time Today: {format_duration(sum(entry.minutes(now) for entry in entries))}")


@app.command()
def edit() -> None:
    """Open today's file in $EDITOR."""
    with _exit_on_error():
        editor = get_editor()
    path = get_log_path(_now()[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    subprocess.run([editor, str(path)])


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"englog {__version__}")


if __name__ == "__main__":
    app()
