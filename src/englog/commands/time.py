"""Time tracking commands for englog."""

import typer

from englog.core.tags import extract_tags_from_text, format_tags
from englog.core.timer import (
    calculate_total_time,
    find_timer_by_description,
    find_timer_by_number,
    list_timers,
    pause_timer,
    resume_timer,
    start_timer,
    stop_timer,
)
from englog.utils.formatting import format_duration

app = typer.Typer(help="Time tracking commands")


@app.command()
def start(
    task: str = typer.Argument(..., help="Task description with @tags, or timer number"),
) -> None:
    """Start tracking time (auto-stops current timer)."""
    # Check if task is a number (restart by number)
    try:
        timer_num = int(task)
        existing = find_timer_by_number(timer_num)
        if not existing:
            typer.echo(f"Error: Timer #{timer_num} not found", err=True)
            raise typer.Exit(1)

        stopped, new_timer = start_timer(existing.description, existing.tags)
        if stopped:
            typer.echo(
                f"Stopped: {stopped.description} ({format_duration(stopped.duration_minutes)}), "
                f"Started: {new_timer.description}"
            )
        else:
            typer.echo(f"Started: {new_timer.description}")
        return
    except ValueError:
        pass

    # Parse description and tags
    description, tags = extract_tags_from_text(task)

    if not description:
        typer.echo("Error: Task description cannot be empty", err=True)
        raise typer.Exit(1)

    # Check if description matches existing timer
    existing = find_timer_by_description(description)
    if existing:
        # Restart with original tags
        stopped, new_timer = start_timer(existing.description, existing.tags)
    else:
        # New timer
        stopped, new_timer = start_timer(description, tags)

    if stopped:
        typer.echo(
            f"Stopped: {stopped.description} ({format_duration(stopped.duration_minutes)}), "
            f"Started: {new_timer.description}"
        )
    else:
        typer.echo(f"Started: {new_timer.description}")


@app.command()
def stop() -> None:
    """Stop and log current timer."""
    try:
        timer = stop_timer()
        typer.echo(f"Stopped: {timer.description} ({format_duration(timer.duration_minutes)})")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def pause() -> None:
    """Pause current timer."""
    try:
        timer = pause_timer()
        typer.echo(f"Paused: {timer.description} ({format_duration(timer.duration_minutes)})")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def resume() -> None:
    """Resume paused timer."""
    try:
        timer = resume_timer()
        typer.echo(f"Resumed: {timer.description}")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="list")
def list_cmd() -> None:
    """List all timers from today."""
    timers = list_timers()

    if not timers:
        typer.echo("No timers today")
        return

    typer.echo("")
    for timer in timers:
        tags_str = format_tags(timer.tags)
        status = ""
        if timer.is_active:
            status = " [ACTIVE]"
        elif timer.is_paused:
            status = " [PAUSED]"

        typer.echo(
            f"{timer.number}. {timer.description} {tags_str} ({format_duration(timer.duration_minutes)}){status}"
        )

    typer.echo("")
    total = calculate_total_time()
    typer.echo(f"Total: {format_duration(total)}")
