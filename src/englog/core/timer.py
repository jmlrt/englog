"""Timer state management for englog."""

import re
from dataclasses import dataclass
from datetime import date

from englog.core.file import (
    append_to_section,
    get_section_content,
    read_daily_file,
    write_daily_file,
)
from englog.core.tags import format_tags, parse_tags
from englog.utils.formatting import (
    calculate_duration_minutes,
    format_duration,
    get_current_time,
    parse_duration,
)


@dataclass
class TimerEntry:
    """Represents a time tracking entry."""

    number: int
    description: str
    tags: list[str]
    start_time: str
    end_time: str | None  # None if active
    duration_minutes: int
    is_active: bool
    is_paused: bool = False
    paused_duration: int = 0  # Minutes paused


def get_active_timer(for_date: date | None = None) -> TimerEntry | None:
    """Get currently active timer from today's file."""
    return next((t for t in list_timers(for_date) if t.is_active), None)


def get_paused_timer(for_date: date | None = None) -> TimerEntry | None:
    """Get currently paused timer from today's file."""
    return next((t for t in list_timers(for_date) if t.is_paused), None)


def start_timer(
    description: str, tags: list[str], for_date: date | None = None
) -> tuple[TimerEntry | None, TimerEntry]:
    """Start new timer, auto-stop active timer if exists. Returns (stopped_timer, new_timer)."""
    stopped = None
    active = get_active_timer(for_date)

    if active:
        stopped = stop_timer(for_date)

    # Create new timer entry
    current_time = get_current_time()
    tags_str = format_tags(tags)
    entry_content = (
        f"### {current_time} - [ACTIVE] | {description} | {tags_str}\n- Duration: 0m (running)"
    )

    append_to_section("Time", entry_content, for_date)

    new_timer = TimerEntry(
        number=len(list_timers(for_date)),
        description=description,
        tags=tags,
        start_time=current_time,
        end_time=None,
        duration_minutes=0,
        is_active=True,
    )

    return stopped, new_timer


def stop_timer(for_date: date | None = None) -> TimerEntry:
    """Stop active timer and log duration."""
    active = get_active_timer(for_date)
    if not active:
        raise ValueError("No active timer")

    current_time = get_current_time()
    duration = calculate_duration_minutes(active.start_time, current_time)
    # Subtract any paused time
    duration = max(0, duration - active.paused_duration)

    # Update the timer entry in the file
    _update_timer_entry(active, current_time, duration, for_date)

    active.end_time = current_time
    active.duration_minutes = duration
    active.is_active = False
    active.is_paused = False

    return active


def pause_timer(for_date: date | None = None) -> TimerEntry:
    """Pause active timer."""
    active = get_active_timer(for_date)
    if not active:
        raise ValueError("No active timer")
    if active.is_paused:
        raise ValueError("Timer is already paused")

    # Update file to mark as paused
    _mark_timer_paused(active, for_date)

    active.is_paused = True
    return active


def resume_timer(for_date: date | None = None) -> TimerEntry:
    """Resume paused timer."""
    paused = get_paused_timer(for_date)
    if not paused:
        raise ValueError("No paused timer to resume")

    # Update file to mark as active
    _mark_timer_resumed(paused, for_date)

    paused.is_paused = False
    return paused


def list_timers(for_date: date | None = None) -> list[TimerEntry]:
    """List all timers from today with numbers."""
    content = get_section_content("Time", for_date)
    if not content:
        return []

    timers = []
    # Pattern to match timer entries
    # Format: ### HH:MM - HH:MM | description | @tags OR ### HH:MM - [ACTIVE] | description | @tags
    pattern = r"### (\d{2}:\d{2}) - (\[ACTIVE\]|\[PAUSED\]|\d{2}:\d{2}) \| ([^|]+) \| ([^\n]*)\n- Duration: ([^\n]+)"

    for idx, match in enumerate(re.finditer(pattern, content), 1):
        start_time = match.group(1)
        end_or_status = match.group(2)
        description = match.group(3).strip()
        tags_str = match.group(4).strip()
        duration_str = match.group(5).strip()

        tags = parse_tags(tags_str)
        is_active = end_or_status == "[ACTIVE]"
        is_paused = end_or_status == "[PAUSED]"
        end_time = None if is_active or is_paused else end_or_status

        # Parse duration, handle "(running)" suffix
        duration_str_clean = duration_str.replace(" (running)", "").replace(" (paused)", "")
        duration = parse_duration(duration_str_clean)

        # For active timer, calculate current duration
        if is_active:
            duration = calculate_duration_minutes(start_time, get_current_time())
            # Check for paused duration in the entry
            paused_match = re.search(r"paused: (\d+)m", content[match.start() :])
            if paused_match:
                duration -= int(paused_match.group(1))

        timers.append(
            TimerEntry(
                number=idx,
                description=description,
                tags=tags,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration,
                is_active=is_active,
                is_paused=is_paused,
            )
        )

    return timers


def find_timer_by_description(description: str, for_date: date | None = None) -> TimerEntry | None:
    """Find most recent timer matching description (for restart)."""
    timers = list_timers(for_date)
    # Search in reverse order to find most recent
    for timer in reversed(timers):
        if timer.description.lower() == description.lower():
            return timer
    return None


def find_timer_by_number(number: int, for_date: date | None = None) -> TimerEntry | None:
    """Find timer by list number (for restart)."""
    timers = list_timers(for_date)
    for timer in timers:
        if timer.number == number:
            return timer
    return None


def calculate_total_time(for_date: date | None = None) -> int:
    """Calculate total time tracked today in minutes."""
    total = 0
    for timer in list_timers(for_date):
        if timer.is_active:
            duration = calculate_duration_minutes(timer.start_time, get_current_time())
            total += max(0, duration - timer.paused_duration)
        else:
            total += timer.duration_minutes
    return total


def _update_timer_entry(
    timer: TimerEntry, end_time: str, duration: int, for_date: date | None = None
) -> None:
    """Update a timer entry in the file with end time and duration."""
    content = read_daily_file(for_date)
    tags_str = format_tags(timer.tags)

    # Find and replace the active timer entry
    old_pattern = rf"### {re.escape(timer.start_time)} - \[ACTIVE\] \| {re.escape(timer.description)} \| {re.escape(tags_str)}\n- Duration: [^\n]+"
    old_paused_pattern = rf"### {re.escape(timer.start_time)} - \[PAUSED\] \| {re.escape(timer.description)} \| {re.escape(tags_str)}\n- Duration: [^\n]+"

    new_entry = f"### {timer.start_time} - {end_time} | {timer.description} | {tags_str}\n- Duration: {format_duration(duration)}"

    new_content = re.sub(old_pattern, new_entry, content)
    if new_content == content:
        # Try paused pattern
        new_content = re.sub(old_paused_pattern, new_entry, content)

    write_daily_file(new_content, for_date)


def _mark_timer_paused(timer: TimerEntry, for_date: date | None = None) -> None:
    """Mark a timer as paused in the file."""
    content = read_daily_file(for_date)
    tags_str = format_tags(timer.tags)

    # Calculate current duration
    current_duration = calculate_duration_minutes(timer.start_time, get_current_time())

    old_pattern = rf"### {re.escape(timer.start_time)} - \[ACTIVE\] \| {re.escape(timer.description)} \| {re.escape(tags_str)}\n- Duration: [^\n]+"
    new_entry = f"### {timer.start_time} - [PAUSED] | {timer.description} | {tags_str}\n- Duration: {format_duration(current_duration)} (paused)"

    new_content = re.sub(old_pattern, new_entry, content)
    write_daily_file(new_content, for_date)


def _mark_timer_resumed(timer: TimerEntry, for_date: date | None = None) -> None:
    """Mark a paused timer as active again in the file."""
    content = read_daily_file(for_date)
    tags_str = format_tags(timer.tags)

    old_pattern = rf"### {re.escape(timer.start_time)} - \[PAUSED\] \| {re.escape(timer.description)} \| {re.escape(tags_str)}\n- Duration: [^\n]+"
    new_entry = f"### {timer.start_time} - [ACTIVE] | {timer.description} | {tags_str}\n- Duration: {format_duration(timer.duration_minutes)} (running)"

    new_content = re.sub(old_pattern, new_entry, content)
    write_daily_file(new_content, for_date)
