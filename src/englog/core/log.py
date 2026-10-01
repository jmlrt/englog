"""Daily time log.

A day is a `YYYY-MM-DD.txt` file with one `HH:MM title` line per entry. An entry ends when the
next line starts; `HH:MM stop` ends the running entry without starting another. Durations are
never stored, only computed.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from englog.core.config import get_englog_dir

STOP = "stop"


@dataclass(frozen=True)
class Line:
    minute: int  # minutes since midnight
    title: str  # STOP marks the end of the running entry


@dataclass(frozen=True)
class Entry:
    start: int
    end: int | None  # None while running
    title: str

    def minutes(self, now: int) -> int:
        end = now if self.end is None else self.end
        return max(0, end - self.start)


def parse_time(text: str) -> int:
    """Parse HH:MM (or H:MM) into minutes since midnight."""
    hours_text, separator, minutes_text = text.partition(":")
    if not (separator and hours_text.isdigit() and minutes_text.isdigit()):
        raise ValueError(f"Invalid time '{text}', expected HH:MM")
    hours, minutes = int(hours_text), int(minutes_text)
    if len(minutes_text) != 2 or hours > 23 or minutes > 59:
        raise ValueError(f"Invalid time '{text}', expected HH:MM")
    return hours * 60 + minutes


def format_time(minute: int) -> str:
    hours, minutes = divmod(minute, 60)
    return f"{hours:02d}:{minutes:02d}"


def get_log_path(day: date) -> Path:
    return get_englog_dir() / f"{day.isoformat()}.txt"


def parse_lines(text: str, source: str) -> list[Line]:
    """Parse a daily file, failing on malformed, out-of-order or dangling-stop lines."""
    lines: list[Line] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        time_text, _, title = raw.strip().partition(" ")
        try:
            minute = parse_time(time_text)
        except ValueError as error:
            raise ValueError(f"{source}:{number}: {error}") from error
        title = title.strip()
        if not title:
            raise ValueError(f"{source}:{number}: missing title after {time_text}")
        if lines and minute < lines[-1].minute:
            raise ValueError(f"{source}:{number}: {time_text} is earlier than the previous line")
        if title == STOP and (not lines or lines[-1].title == STOP):
            raise ValueError(f"{source}:{number}: stop without a running entry")
        lines.append(Line(minute, title))
    return lines


def read_lines(day: date) -> list[Line]:
    path = get_log_path(day)
    if not path.exists():
        return []
    return parse_lines(path.read_text(), str(path))


def build_entries(lines: list[Line]) -> list[Entry]:
    """Turn lines into entries; each ends at the next line, the last one stays running."""
    entries = []
    for index, line in enumerate(lines):
        if line.title == STOP:
            continue
        end = lines[index + 1].minute if index + 1 < len(lines) else None
        entries.append(Entry(line.minute, end, line.title))
    return entries


def find_running(entries: list[Entry]) -> Entry | None:
    return entries[-1] if entries and entries[-1].end is None else None


def _check_time(lines: list[Line], at: int, now: int) -> None:
    if at > now:
        raise ValueError(f"{format_time(at)} is in the future")
    if lines and at < lines[-1].minute:
        raise ValueError(
            f"{format_time(at)} is earlier than the last line ({format_time(lines[-1].minute)}); "
            "use 'englog edit' to insert it"
        )


def _append(day: date, line: Line) -> None:
    path = get_log_path(day)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(f"{text}{format_time(line.minute)} {line.title}\n")


def start_entry(day: date, title: str, at: int, now: int) -> Entry | None:
    """Append a start line; return the entry it ended, if one was running."""
    if not title:
        raise ValueError("Title cannot be empty")
    if title == STOP:
        raise ValueError(f"'{STOP}' is reserved, use 'englog stop'")
    if "\n" in title or "\r" in title:
        raise ValueError("Title cannot contain a newline")
    lines = read_lines(day)
    _check_time(lines, at, now)
    running = find_running(build_entries(lines))
    _append(day, Line(at, title))
    return Entry(running.start, at, running.title) if running else None


def stop_entry(day: date, at: int, now: int) -> Entry:
    """Append a stop line and return the entry it ended."""
    lines = read_lines(day)
    running = find_running(build_entries(lines))
    if running is None:
        raise ValueError("No running entry")
    _check_time(lines, at, now)
    _append(day, Line(at, STOP))
    return Entry(running.start, at, running.title)
