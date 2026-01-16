"""Daily file operations for englog."""

import re
from datetime import date
from pathlib import Path

from englog.core.config import get_englog_dir
from englog.utils.formatting import get_today_date

# Section order in daily file
SECTIONS = ["Time", "Todo", "TIL", "Notes", "Scratch"]


def get_daily_file_path(for_date: date | None = None) -> Path:
    """Get path to daily file, defaults to today."""
    if for_date is None:
        date_str = get_today_date()
    else:
        date_str = for_date.strftime("%Y-%m-%d")
    return get_englog_dir() / f"{date_str}.md"


def ensure_daily_file_exists(for_date: date | None = None) -> Path:
    """Create daily file if it doesn't exist, return path."""
    file_path = get_daily_file_path(for_date)

    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        if for_date is None:
            date_str = get_today_date()
        else:
            date_str = for_date.strftime("%Y-%m-%d")
        file_path.write_text(f"# {date_str}\n")

    return file_path


def read_daily_file(for_date: date | None = None) -> str:
    """Read daily file content. Returns empty string if file doesn't exist."""
    file_path = get_daily_file_path(for_date)
    if not file_path.exists():
        return ""
    return file_path.read_text()


def write_daily_file(content: str, for_date: date | None = None) -> None:
    """Write content to daily file."""
    file_path = ensure_daily_file_exists(for_date)
    file_path.write_text(content)


def get_section_content(section: str, for_date: date | None = None) -> str:
    """Get content of a specific section from daily file."""
    content = read_daily_file(for_date)
    if not content:
        return ""

    # Find section start
    section_pattern = rf"^## {re.escape(section)}\s*$"
    match = re.search(section_pattern, content, re.MULTILINE)
    if not match:
        return ""

    start = match.end()

    # Find next section or end of file
    next_section_pattern = r"^## \w+"
    next_match = re.search(next_section_pattern, content[start:], re.MULTILINE)
    if next_match:
        end = start + next_match.start()
    else:
        end = len(content)

    return content[start:end].strip()


def append_to_section(section: str, content: str, for_date: date | None = None) -> None:
    """Append content to a section, create section if needed."""
    file_path = ensure_daily_file_exists(for_date)
    file_content = file_path.read_text()

    # Check if section exists
    section_pattern = rf"^## {re.escape(section)}\s*$"
    match = re.search(section_pattern, file_content, re.MULTILINE)

    if match:
        # Find insertion point (end of section)
        start = match.end()

        # Find next section
        next_section_pattern = r"^## \w+"
        next_match = re.search(next_section_pattern, file_content[start:], re.MULTILINE)

        if next_match:
            insert_pos = start + next_match.start()
            # Insert before next section with proper spacing
            new_content = (
                file_content[:insert_pos].rstrip()
                + "\n\n"
                + content
                + "\n\n"
                + file_content[insert_pos:]
            )
        else:
            # Append at end
            new_content = file_content.rstrip() + "\n\n" + content + "\n"
    else:
        # Create section in correct order
        insert_position = _find_section_insert_position(file_content, section)
        if insert_position == len(file_content):
            new_content = file_content.rstrip() + f"\n\n## {section}\n\n" + content + "\n"
        else:
            new_content = (
                file_content[:insert_position].rstrip()
                + f"\n\n## {section}\n\n"
                + content
                + "\n\n"
                + file_content[insert_position:]
            )

    file_path.write_text(new_content)


def _find_section_insert_position(content: str, section: str) -> int:
    """Find position to insert a new section to maintain correct order."""
    section_idx = SECTIONS.index(section) if section in SECTIONS else len(SECTIONS)

    # Find the first section that should come after this one
    for later_section in SECTIONS[section_idx + 1 :]:
        pattern = rf"^## {re.escape(later_section)}\s*$"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.start()

    return len(content)


def replace_section_content(section: str, new_content: str, for_date: date | None = None) -> None:
    """Replace entire content of a section."""
    file_path = ensure_daily_file_exists(for_date)
    file_content = file_path.read_text()

    section_pattern = rf"^## {re.escape(section)}\s*$"
    match = re.search(section_pattern, file_content, re.MULTILINE)

    if not match:
        # Section doesn't exist, create it
        append_to_section(section, new_content, for_date)
        return

    start = match.end()

    # Find next section
    next_section_pattern = r"^## \w+"
    next_match = re.search(next_section_pattern, file_content[start:], re.MULTILINE)

    if next_match:
        end = start + next_match.start()
        result = (
            file_content[: match.start()]
            + f"## {section}\n\n"
            + new_content
            + "\n\n"
            + file_content[end:]
        )
    else:
        result = file_content[: match.start()] + f"## {section}\n\n" + new_content + "\n"

    file_path.write_text(result)
