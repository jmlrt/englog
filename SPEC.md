# englog - Specification

## Overview

A minimal CLI to log a workday as time entries in a plain text file. Fast capture, human-editable,
processed elsewhere.

## Principles

- **Fast capture**: one short command, no prompts, no quoting needed for the title
- **Plain text**: one line per entry, greppable, fixable in any editor
- **Nothing derived is stored**: durations are computed on read, so they can't drift from the timestamps
- **Convention over configuration**: only `$ENGLOG_DIR` and `$EDITOR`, no config files

## File format

`$ENGLOG_DIR/YYYY-MM-DD.txt`, local time, one line per entry:

```
HH:MM title
HH:MM stop
```

- `HH:MM` is 24h; `H:MM` is also accepted when reading.
- The title is everything after the first space and may contain any text except a newline.
- `stop` is the only marker. A title can't be exactly `stop`.
- An entry runs from its time to the time of the next line. A `stop` line ends the running entry
  without starting another, so entries after a `stop` leave a gap.
- The last line is the running entry unless it is a `stop`.
- Blank lines are ignored. The date comes from the filename.
- Entries don't cross midnight: a new day is a new file.

### Validation (reading)

Reading fails with `<file>:<line>: <reason>` on:

- a line that doesn't start with a valid time
- a missing title
- a time earlier than the previous line (equal times are allowed)
- a `stop` with no running entry (first line, or right after another `stop`)

## Commands

```
englog start [--at HH:MM] TITLE...   Start an entry; ends the running one
englog stop [--at HH:MM]             End the running entry
englog list                          Today's entries with durations and total
englog status                        Running entry and today's total
englog edit                          Open today's file in $EDITOR
englog version
```

- `--at` is only parsed before the title; everything after it is the title, joined with spaces.
- `--at` can't be in the future or earlier than the last line (error: use `englog edit`).
- `start` rejects an empty title, `stop` as a title, and a title containing a newline.
- `stop` with no running entry is an error.
- Durations print as `45m`, `1h`, `1h 5m`.

### Output

```
$ englog start 1/1 alice
Stopped: day prep (30m), Started: 1/1 alice

$ englog stop
Stopped: 1/1 alice (1h 5m)

$ englog list
08:00-08:30 day prep (30m)
08:30-09:35 1/1 alice (1h 5m)

Total: 1h 35m

$ englog status
Running: none
Time Today: 1h 35m
```

A running entry is listed as `HH:MM-now` and `status` shows `Running: <title> (since HH:MM, <elapsed>)`.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENGLOG_DIR` | Directory for daily files | `~/englog` |
| `EDITOR` | Editor for `englog edit` | (required for that command) |
