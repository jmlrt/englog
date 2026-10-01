# englog

Minimalist CLI to log your workday as time entries in a plain text file. Optimized for speed of capture,
not processing.

## Installation

```bash
git clone https://github.com/jmlrt/englog.git
cd englog

# Install globally from the checkout
uv tool install -e .
```

### Setup

```bash
# Directory for daily files (optional, defaults to ~/englog)
export ENGLOG_DIR=~/Documents/englog

# Editor for `englog edit` (required for that command)
export EDITOR=vim
```

## Usage

```bash
englog start day prep, check notifs     # Start an entry (ends the running one), no quotes needed
englog start --at 14:20 1/1 alice       # Forgot to log: start at a past time
englog stop                             # End the running entry
englog stop --at 17:45                  # End it at a past time
englog list                             # Today's entries with durations
englog status                           # Running entry and today's total
englog edit                             # Open today's file in $EDITOR
```

- `--at HH:MM` is only accepted before the title; everything after it is the title.
- Characters the shell treats specially (`( ) ; & | < > * ? '` and `"`) still need quoting.
- The time can't be in the future or earlier than the last line. Use `englog edit` for anything else.

```bash
$ englog list
08:00-08:30 day prep, check notifs (30m)
08:30-now 1/1 alice (1h 5m)

Total: 1h 35m
```

## File format

`$ENGLOG_DIR/YYYY-MM-DD.txt`, one `HH:MM title` line per entry:

```
08:00 day prep, check notifs
08:30 1/1 alice
09:30 stop
10:00 shallow work
```

- An entry ends when the next line starts. Durations are never stored, only computed.
- `HH:MM stop` ends the running entry. Use it for breaks and at the end of the day.
- The last line is the running entry unless it is a `stop`.
- Lines must be in chronological order. A malformed file makes `list` and `status` fail with the line number.
- Fixing a time or a title means editing one line with `englog edit`.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENGLOG_DIR` | Directory for daily files | `~/englog` |
| `EDITOR` | Editor for `englog edit` | (required for that command) |

## License

MIT
