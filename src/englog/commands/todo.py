"""Todo management commands for englog."""

import typer

from englog.core.tags import extract_tags_from_text, format_tags
from englog.core.todo import (
    add_todo,
    find_todo_by_description,
    find_todo_by_number,
    list_todos_with_numbers,
    move_todo,
)

app = typer.Typer(help="Todo management commands")


def _move_to_section(task: str, target: str) -> None:
    """Move task to target section by number or description."""
    # Try by number first
    if task.isdigit():
        existing = find_todo_by_number(int(task))
        if not existing:
            typer.echo(f"Error: Task #{task} not found in Todo or Doing sections", err=True)
            raise typer.Exit(1)
        if existing.section == target:
            typer.echo(f"Task is already in {target}: {existing.description}")
            return
        move_todo(existing, target)
        typer.echo(f"{target}: {existing.description}")
        return

    # Try by description
    description, tags = extract_tags_from_text(task)
    existing = find_todo_by_description(description)

    if existing:
        if existing.section == "Done" and target != "Done":
            typer.echo(f"Error: Cannot move completed task: {existing.description}", err=True)
            raise typer.Exit(1)
        if existing.section == target:
            typer.echo(f"Task is already in {target}: {existing.description}")
            return
        move_todo(existing, target)
        typer.echo(f"{target}: {existing.description}")
    else:
        add_todo(description, tags, target)
        typer.echo(f"{target}: {description}")


@app.command()
def add(task: str = typer.Argument(..., help="Task description with @tags")) -> None:
    """Add a new todo."""
    description, tags = extract_tags_from_text(task)
    if not description:
        typer.echo("Error: Task description cannot be empty", err=True)
        raise typer.Exit(1)
    add_todo(description, tags, "Todo")
    typer.echo(f"Added: {description}")


@app.command()
def doing(task: str = typer.Argument(..., help="Task description or number")) -> None:
    """Move task to doing (by description match or number)."""
    _move_to_section(task, "Doing")


@app.command()
def done(task: str = typer.Argument(..., help="Task description or number")) -> None:
    """Mark task as completed (by description match or number)."""
    _move_to_section(task, "Done")


@app.command(name="list")
def list_cmd() -> None:
    """List all todos with numbers."""
    todos = list_todos_with_numbers()

    if not todos:
        typer.echo("No todos today")
        return

    typer.echo("")

    # Group by section
    current_section = None
    for todo in todos:
        if todo.section != current_section:
            current_section = todo.section
            typer.echo(f"{current_section}:")

        tags_str = format_tags(todo.tags)
        if todo.number is not None:
            typer.echo(f"  {todo.number}. {todo.description} {tags_str}")
        else:
            typer.echo(f"  - {todo.description} {tags_str}")

    typer.echo("")
