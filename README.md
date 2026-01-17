# englog

Minimalist CLI for engineering workdays. Capture time tracking, todos, TILs, and notes as timestamped markdown. Optimized for speed, not processing.

## Philosophy

- **Fast capture**: Minimal typing, no prompts, no friction
- **Markdown-first**: Human-readable, editor-agnostic, greppable
- **Processing elsewhere**: Files designed for external tools/editors
- **Daily ephemeral storage**: Entries captured during the day, processed end-of-day into permanent systems

## Installation

```bash
# Clone the repository
git clone https://github.com/jmlrt/englog.git
cd englog

# Install with uv
uv sync

# Or install globally
uv tool install -e .
```

### Setup

```bash
# Set up englog directory (optional, defaults to ~/englog)
export ENGLOG_DIR=~/Documents/englog

# Set up editor (required for --edit commands)
export EDITOR=vim  # or nano, code --wait, etc.

# Add to your shell profile for persistence
echo 'export ENGLOG_DIR=~/Documents/englog' >> ~/.zshrc
echo 'export EDITOR=vim' >> ~/.zshrc

# Initialize
englog init

# Optional: create a short alias
echo 'alias el="englog"' >> ~/.zshrc
```

## Quick Start

```bash
# Start tracking time
englog time start "Review PRs @code-review"

# Add a todo
englog todo add "Fix auth bug @backend @urgent"

# Capture a learning
englog til "Python dataclasses support frozen=True @python"

# Quick note
englog note "New staging URL: https://staging.example.com @reference"

# Check status
englog status

# Open today's file in editor
englog edit
```

## Commands

### Time Tracking

```bash
englog time start "task description @tag1 @tag2"   # Start tracking time
englog time start 3                                # Restart timer by number
englog time pause                                  # Pause current timer
englog time resume                                 # Resume paused timer
englog time stop                                   # Stop and log current timer
englog time list                                   # List all timers from today
```

**Features:**
- Auto-stops current timer when starting a new one
- Restart by number creates a new entry (preserves timeline)
- Shows total time at bottom of list

**Example session:**
```bash
$ englog time start "Fix auth bug @backend"
Started: Fix auth bug

$ englog time start "Review security PR @code-review"
Stopped: Fix auth bug (1h 23m), Started: Review security PR

$ englog time list
1. Fix auth bug @backend (1h 23m)
2. Review security PR @code-review (45m) [ACTIVE]

Total: 2h 8m
```

### Todo Management

```bash
englog todo add "task description @tag1 @tag2"     # Add to todo list
englog todo doing "task description"               # Move to doing by description
englog todo doing 2                                # Move to doing by number
englog todo done "task description"                # Mark as completed
englog todo done 3                                 # Mark as completed by number
englog todo list                                   # List all todos
```

**Features:**
- Match by description (case-insensitive) or by number
- Numbers only assigned to Todo and Doing sections
- Direct to done: `englog todo done "Quick fix"` adds directly if no match

**Example session:**
```bash
$ englog todo add "Fix auth bug @backend"
Added: Fix auth bug

$ englog todo add "Update docs @documentation"
Added: Update docs

$ englog todo list
Todo:
  1. Fix auth bug @backend
  2. Update docs @documentation

$ englog todo doing 1
Doing: Fix auth bug

$ englog todo done 1
Done: Fix auth bug
```

### TIL (Today I Learned)

```bash
englog til "quick learning note @tag1 @tag2"       # Single-line TIL
englog til --edit @tag1 @tag2                      # Multi-line TIL (opens $EDITOR)
```

Capture learnings, techniques, patterns, "aha moments" - knowledge worth remembering.

### Notes

```bash
englog note "quick note @tag1 @tag2"               # Single-line note
englog note --edit @tag1 @tag2                     # Multi-line note (opens $EDITOR)
```

Capture important context, references, team updates, URLs, API endpoints.

### Scratch

```bash
englog scratch "temporary capture @tag1"           # Single-line scratch
englog scratch --edit @tag1                        # Multi-line scratch (opens $EDITOR)
```

Ultra-ephemeral captures - error messages, debug output, things you need RIGHT NOW.

### Utility Commands

```bash
englog init                                        # Initialize englog directory
englog status                                      # Show overview
englog edit                                        # Open today's file in $EDITOR
englog version                                     # Show version
englog --help                                      # Show help
```

## Tags

Tags use `@tagname` format and work consistently across all commands:

```bash
englog time start "Fix auth @api-refactor @backend @security"
englog todo add "Review PR @api-refactor @code-review"
englog til "OAuth handles token refresh @api-refactor @security"
englog note "API endpoint: https://api.example.com @api @reference"
```

Valid tag characters: `a-z`, `A-Z`, `0-9`, `-`, `_`

## File Format

All data stored in daily markdown files at `$ENGLOG_DIR/YYYY-MM-DD.md`:

```markdown
# 2025-01-15

## Time

### 09:23 - 10:46 | Fix auth endpoints | @api-refactor @backend
- Duration: 1h 23m

### 10:46 - [ACTIVE] | Review security PR | @code-review
- Duration: 45m (running)

## Todo

### Todo
- [14:20] Update documentation @docs @api

### Doing
- [09:45] Fix authentication bug @backend @security

### Done
- [11:30] Deploy staging environment @devops

## TIL

### 10:15 | @python @performance
Python's walrus operator can simplify list comprehensions.

## Notes

### 09:15 | @api @reference
API endpoint: https://api.example.com/v2/users

## Scratch

### 11:00 | @error @debugging
Error output from failed deployment...
```

## End-of-Day Workflow

1. **During the day**: Rapid capture with `englog` commands
2. **End of day**: Review with `englog status` and `englog edit`
3. **Process entries**: Extract to permanent systems (task tracker, knowledge base)
4. **Archive or delete**: Daily files are ephemeral by design

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENGLOG_DIR` | Directory for daily files | `~/englog` |
| `EDITOR` | Editor for `--edit` and `englog edit` | (required) |

## License

MIT
