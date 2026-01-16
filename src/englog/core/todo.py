"""Todo matching and listing logic for englog."""

import re
from dataclasses import dataclass
from datetime import date

from englog.core.file import get_section_content, replace_section_content
from englog.core.tags import format_tags, parse_tags
from englog.utils.formatting import get_current_time


@dataclass
class TodoEntry:
    """Represents a todo entry."""

    number: int | None  # None for Done items
    description: str
    tags: list[str]
    timestamp: str
    section: str  # "Todo", "Doing", or "Done"


def add_todo(
    description: str,
    tags: list[str],
    section: str = "Todo",
    for_date: date | None = None,
) -> TodoEntry:
    """Add a new todo entry to specified section."""
    timestamp = get_current_time()

    # Get current section content and add new entry
    todos = _parse_all_todos(for_date)
    todos.append(
        TodoEntry(
            number=None,  # Will be assigned when listing
            description=description,
            tags=tags,
            timestamp=timestamp,
            section=section,
        )
    )

    _write_todos(todos, for_date)

    return TodoEntry(
        number=None,
        description=description,
        tags=tags,
        timestamp=timestamp,
        section=section,
    )


def find_todo_by_description(description: str, for_date: date | None = None) -> TodoEntry | None:
    """Find todo by exact description match (case-insensitive)."""
    todos = _parse_all_todos(for_date)
    for todo in todos:
        if todo.description.lower() == description.lower():
            return todo
    return None


def find_todo_by_number(number: int, for_date: date | None = None) -> TodoEntry | None:
    """Find todo by display number in Todo or Doing sections only."""
    todos = list_todos_with_numbers(for_date)
    for todo in todos:
        if todo.number == number:
            return todo
    return None


def move_todo(entry: TodoEntry, target_section: str, for_date: date | None = None) -> TodoEntry:
    """Move entry to target section with new timestamp."""
    todos = _parse_all_todos(for_date)

    # Remove from current location
    todos = [
        t
        for t in todos
        if not (t.description.lower() == entry.description.lower() and t.section == entry.section)
    ]

    # Add to new section with new timestamp
    new_entry = TodoEntry(
        number=None,
        description=entry.description,
        tags=entry.tags,
        timestamp=get_current_time(),
        section=target_section,
    )
    todos.append(new_entry)

    _write_todos(todos, for_date)
    return new_entry


def list_todos_with_numbers(for_date: date | None = None) -> list[TodoEntry]:
    """List todos with numbers for Todo and Doing sections only."""
    todos = _parse_all_todos(for_date)

    # Assign numbers to Todo and Doing items only
    number = 1
    result = []
    for section in ["Todo", "Doing"]:
        for todo in todos:
            if todo.section == section:
                todo.number = number
                number += 1
                result.append(todo)

    # Add Done items without numbers
    for todo in todos:
        if todo.section == "Done":
            result.append(todo)

    return result


def get_todo_counts(for_date: date | None = None) -> dict[str, int]:
    """Get counts of todos in each section."""
    todos = _parse_all_todos(for_date)
    counts = {"Todo": 0, "Doing": 0, "Done": 0}
    for todo in todos:
        if todo.section in counts:
            counts[todo.section] += 1
    return counts


def _parse_all_todos(for_date: date | None = None) -> list[TodoEntry]:
    """Parse all todos from the Todo section."""
    content = get_section_content("Todo", for_date)
    if not content:
        return []

    todos = []
    current_section = None

    for line in content.split("\n"):
        line = line.strip()

        # Check for subsection headers
        if line == "### Todo":
            current_section = "Todo"
            continue
        elif line == "### Doing":
            current_section = "Doing"
            continue
        elif line == "### Done":
            current_section = "Done"
            continue

        # Parse todo entries
        if line.startswith("- [") and current_section:
            match = re.match(r"- \[(\d{2}:\d{2})\] (.+)", line)
            if match:
                timestamp = match.group(1)
                rest = match.group(2)

                # Extract tags from the rest
                tags = parse_tags(rest)
                # Remove tags to get description
                description = re.sub(r"@[a-zA-Z0-9_-]+", "", rest).strip()

                todos.append(
                    TodoEntry(
                        number=None,
                        description=description,
                        tags=tags,
                        timestamp=timestamp,
                        section=current_section,
                    )
                )

    return todos


def _write_todos(todos: list[TodoEntry], for_date: date | None = None) -> None:
    """Write all todos back to the file."""
    sections = {"Todo": [], "Doing": [], "Done": []}

    for todo in todos:
        tags_str = format_tags(todo.tags)
        line = f"- [{todo.timestamp}] {todo.description} {tags_str}".strip()
        sections[todo.section].append(line)

    content_parts = []
    for section_name in ["Todo", "Doing", "Done"]:
        content_parts.append(f"### {section_name}")
        for line in sections[section_name]:
            content_parts.append(line)

    content = "\n".join(content_parts)
    replace_section_content("Todo", content, for_date)
