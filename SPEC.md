# englog - Specification

## Overview
A minimalist CLI tool for software engineers to quickly capture workday data as timestamped markdown files. Optimized for speed of capture, not processing.

## Core Philosophy
- **Fast capture**: Minimal typing, no prompts, no friction
- **Markdown-first**: Human-readable, editor-agnostic, greppable
- **Processing elsewhere**: Files designed for external tools/editors
- **Daily ephemeral storage**: Entries captured during the day, processed end-of-day into permanent systems
- **Consistent tagging**: Tags work the same across all commands for unified categorization
- **Convention over configuration**: Uses environment variables and standards, no config files

## Commands

### Time Tracking
```bash
englog time start "task description @tag1 @tag2"   # Start tracking time (auto-stops current timer)
englog time start 3                                # Restart timer by number (from list)
englog time pause                                  # Pause current timer
englog time resume                                 # Resume paused timer  
englog time stop                                   # Stop and log current timer
englog time list                                   # List all timers from today
```

**Time Tracking Behavior:**

**Starting by description:**
- If description matches existing timer (case-insensitive, tags can differ): restarts with original tags
- If no match: creates new timer entry
- Auto-stops current active timer if any
- **Always creates a new separate entry** (not a continuation)

**Starting by number:**
- Use timer number from `englog time list` output
- Restarts that timer with exact description and tags
- Auto-stops current active timer if any
- **Creates a new separate entry** (not a continuation)

**Time List Output:**
```bash
$ englog time list

1. Fix auth endpoints @api-refactor @backend @security (2h 22m)
2. Debug memory leak @bug-fixes @performance (45m)
3. Fix auth endpoints @api-refactor @backend @security (1h 10m)
4. Review PR #234 @code-review (30m) [ACTIVE]

Total: 4h 47m
```

**Notes on numbering:**
- Numbers assigned to all timers chronologically (completed and active)
- Active timer marked with `[ACTIVE]`
- Same task can appear multiple times as separate entries (different sessions)
- Each entry represents a distinct work session
- Total time shown at bottom (sum of all timers including active)

**Constraints:**
- Single active timer only (starting a new timer automatically stops the current one)
- When auto-stopping, shows: "Stopped: [task] (Xh Ym), Started: [new task]"
- Each restart creates a new time entry (preserves timeline)
- Timer state embedded in markdown file
- Local timezone for all timestamps
- Tags parsed and stored in metadata (consistent with TIL/Notes/Scratch)

**Error Handling:**
- `englog time pause/resume/stop` with no active timer → Error: "No active timer"
- `englog time resume` with no paused timer → Error: "No paused timer to resume"
- `englog time start X` where X is invalid number → Error: "Timer #X not found"
- `englog time list` with no timers today → Shows "No timers today"

**Examples:**
```bash
# Start new timer
$ englog time start "Fix auth bug @backend"
Started: Fix auth bug

# Switch to urgent task (auto-stops current)
$ englog time start "Review security PR @code-review @urgent"
Stopped: Fix auth bug (1h 23m), Started: Review security PR

# Finish urgent task
$ englog time stop
Stopped: Review security PR (45m)

# Check what you worked on today
$ englog time list
1. Fix auth bug @backend (1h 23m)
2. Review security PR @code-review @urgent (45m)

Total: 2h 8m

# Restart by number (creates new entry)
$ englog time start 1
Started: Fix auth bug @backend

# Work for a while...
$ englog time stop
Stopped: Fix auth bug (2h 10m)

# List shows separate entries
$ englog time list
1. Fix auth bug @backend (1h 23m)
2. Review security PR @code-review @urgent (45m)
3. Fix auth bug @backend (2h 10m)

Total: 4h 18m

# Or restart by description (exact match, creates new entry)
$ englog time start "Fix auth bug @backend"
Started: Fix auth bug @backend

# Pause for lunch (within same session)
$ englog time pause
Paused: Fix auth bug (30m)

$ englog time resume
Resumed: Fix auth bug

$ englog time stop
Stopped: Fix auth bug (1h 15m)

# Now have multiple sessions for same task
$ englog time list
1. Fix auth bug @backend (1h 23m)
2. Review security PR @code-review @urgent (45m)
3. Fix auth bug @backend (2h 10m)
4. Fix auth bug @backend (1h 15m)

Total: 5h 33m
```

**Restart creates new entries:**
- Each restart is a **new, separate time entry**
- Preserves timeline of when you actually worked
- Same task can appear multiple times with different durations
- Total time per task calculated in end-of-day processing or future `englog time report` command

**Pause/Resume vs Restart:**
- **Pause/Resume**: Short interruptions within the same work session (lunch, meeting)
- **Restart (by number or description)**: Return to a task later, new session, new entry

**Markdown format:**
```markdown
## Time

### 09:23 - 10:46 | Fix auth bug | @backend
- Duration: 1h 23m

### 10:46 - 11:31 | Review security PR | @code-review @urgent
- Duration: 45m

### 13:00 - 15:10 | Fix auth bug | @backend
- Duration: 2h 10m

### 15:30 - 16:45 | Fix auth bug | @backend
- Duration: 1h 15m
```

**Notes:**
- Same task "Fix auth bug" appears 3 times as separate entries
- Each entry shows exactly when work happened
- Total time per task: 1h 23m + 2h 10m + 1h 15m = 4h 48m (calculated later)
- Honest representation of context switching and work patterns

### Todo Management
```bash
englog todo add "task description @tag1 @tag2"      # Add to todo list
englog todo doing "task description @tag1 @tag2"    # Move to doing by description match
englog todo doing 2                                 # Move to doing by task number
englog todo done "task description @tag1 @tag2"     # Mark as completed by description match
englog todo done 3                                  # Mark as completed by task number
englog todo list                                    # List all todos with numbers
```

**Todo Matching Behavior:**

Two ways to reference todos: **by description** or **by number**

**By description (string argument):**
- Exact match search (case-insensitive, tags can differ)
- Example: `englog todo doing "Fix auth bug"` searches for match in Todo section
- If match found: removes from previous section, adds to new section with current timestamp
- If no match found: simply adds new entry to target section (allows direct to doing/done)

**By number (integer argument):**
- Use task number from `englog todo list` output
- Example: `englog todo doing 2` moves task #2 to Doing
- Searches across Todo and Doing sections only (Done items cannot transition)
- If number not found: Error: "Task #X not found in Todo or Doing sections"
- Numbers are ephemeral (recalculated on each `list` command, not stored in markdown)

**Todo List Output:**
```bash
$ englog todo list

Todo:
  1. Review PR #234 @code-review @api-refactor
  2. Update documentation @docs @api
  3. Fix memory leak @performance @bug

Doing:
  4. Fix authentication bug @backend @security @urgent

Done:
  - Deploy staging environment @devops @deployment
  - Write release notes @documentation @v2.0
```

**Notes on numbering:**
- Numbers assigned only to Todo and Doing sections (items that can transition)
- Done items shown without numbers (cannot transition further)
- Numbers recalculated each time `list` is run
- Section order: Todo → Doing → Done

**Error Handling:**
- `englog todo doing/done X` where X is invalid number → Error: "Task #X not found in Todo or Doing sections"
- `englog todo doing/done X` where X > highest number → Error: "Task #X not found in Todo or Doing sections"
- `englog todo list` with no todos → Shows "No todos today"

**Examples:**
```bash
# Full workflow with description matching
englog todo add "Fix auth bug @backend"
englog todo doing "Fix auth bug @backend"      # Matches & moves from Todo → Doing
englog todo done "Fix auth bug @backend"       # Matches & moves from Doing → Done

# Using numbers (explicit reference)
englog todo add "Review PR"
englog todo add "Update docs"
englog todo list                               # Shows: 1. Review PR, 2. Update docs
englog todo doing 2                            # Moves task #2 to Doing
englog todo list                               # Shows: 1. Review PR (Todo), 2. Update docs (Doing)
englog todo done 2                             # Moves task #2 to Done

# Direct to done (no prior todo)
englog todo done "Quick hotfix @urgent"        # No match, just adds to Done

# Partial workflow
englog todo doing "Debug memory leak"          # No match in Todo, adds to Doing
englog todo done "Debug memory leak"           # Matches from Doing → Done

# Mixing numbered and description matching
englog todo list                               # Check what's there
englog todo doing 1                            # Move by number
englog todo done "Some other task"             # Complete by description

# Tags can differ in description matching
englog todo add "Fix bug @backend"
englog todo done "Fix bug @urgent @backend"    # Still matches (description is same)
```

### TIL (Today I Learned)
```bash
englog til "quick learning note @tag1 @tag2"   # Single-line TIL
englog til --edit @tag1 @tag2                  # Multi-line TIL (opens $EDITOR)
```

**Purpose:** Capture learnings, techniques, patterns, "aha moments" - knowledge you acquired that's worth remembering.

**Input Modes:**
- **Single-line**: Tags parsed from the text itself
```bash
  englog til "Python walrus operator simplifies comprehensions @python @tips"
```

- **Multi-line (no flag)**: Paste multiple lines, tags parsed from text
```bash
  englog til "Git workflow tips:
  - Use rebase for clean history
  - Fixup commits with --fixup
  @git @workflow"
```

- **Editor mode** (`--edit`): Opens `$EDITOR`, tags passed as CLI arguments added to metadata
```bash
  englog til --edit @python @advanced
  # Opens editor, write content, @python @advanced added to metadata on save
```

**Error Handling:**
- `--edit` and `$EDITOR` not set → Error: "EDITOR environment variable not set"
- Empty content after `--edit` → Warning: "Empty content, entry not created"

### Notes
```bash
englog note "quick note @tag1 @tag2"          # Single-line note
englog note --edit @tag1 @tag2                 # Multi-line note (opens $EDITOR)
```

**Purpose:** Dual use case for notes:
1. **Important context/references**: Team updates, org changes, deprecation notices, releases, migration impacts, anything relevant happening around you
2. **Quick captures**: URLs, API endpoints, configuration values, things you need to remember

Tags like `@reference`, `@team-update`, `@config`, `@api` can help distinguish during end-of-day processing.

**Input Modes:**
Same as TIL - single-line, multi-line paste, or `--edit` mode.

**Error Handling:**
- `--edit` and `$EDITOR` not set → Error: "EDITOR environment variable not set"
- Empty content after `--edit` → Warning: "Empty content, entry not created"

### Scratch
```bash
englog scratch "temporary capture @tag1 @tag2"  # Single-line scratch
englog scratch --edit @tag1 @tag2               # Multi-line scratch (opens $EDITOR)
```

**Purpose:** Ultra-ephemeral captures - things you need RIGHT NOW but will likely discard:
- Error messages to investigate immediately
- Debug output
- Temporary command results
- Quick dumps that won't make it to end-of-day processing

**Input Modes:**
Same as TIL/Notes - single-line, multi-line paste, or `--edit` mode.

**Error Handling:**
- `--edit` and `$EDITOR` not set → Error: "EDITOR environment variable not set"
- Empty content after `--edit` → Warning: "Empty content, entry not created"

### Utility
```bash
englog init                            # Initialize englog directory
englog status                          # Show overview: active timer, todo counts, time today
englog edit                            # Open today's file in $EDITOR
englog version                         # Show version
englog --help                          # Show help
```

**Init Command:**
- Creates `$ENGLOG_DIR` directory (or `~/englog` if not set)
- If directory already exists, shows: "englog directory already initialized: [path]"
- Daily files are created automatically on first use each day
- No config file or template files created

**Status Command Output:**
```bash
$ englog status

Active Timer:
  Debug memory leak @bug-fixes @performance
  Started: 13:15 (running 2h 15m)

Time Today: 6h 45m

Todos:
  Todo: 3 tasks
  Doing: 1 task
  Done: 2 tasks
```

If no active timer:
```bash
$ englog status

Active Timer: None

Time Today: 4h 30m

Todos:
  Todo: 3 tasks
  Doing: 1 task
  Done: 2 tasks
```

If no timers yet today:
```bash
$ englog status

Active Timer: None

Time Today: 0h 0m

Todos: No todos today
```

If completely empty (no timers, no todos):
```bash
$ englog status

Active Timer: None

Time Today: 0h 0m

Todos: No todos today
```

**Edit Command:**
- Opens `$ENGLOG_DIR/YYYY-MM-DD.md` in `$EDITOR`
- Creates daily file with basic structure if it doesn't exist

**Version Command:**
```bash
$ englog version
englog 0.1.0
```

**Error Handling:**
- `englog edit` and `$EDITOR` not set → Error: "EDITOR environment variable not set"
- `englog edit` and today's file doesn't exist yet → Creates the file with basic structure, then opens it
- `englog status` with no daily file yet → Shows "Active Timer: None", "Time Today: 0h 0m", and "Todos: No todos today"
- `englog init` and cannot create directory → Error: "Cannot create directory: [path] ([reason])"

## Tags

### Tag Format
- Tags use `@tagname` format (e.g., `@python`, `@my-project-a`, `@kubernetes`)
- Multiple tags allowed per entry
- Tags are case-insensitive but preserved as written
- Valid characters: `@[a-zA-Z0-9-_]+`
- No tag validation - keep it simple

### Tag Usage
- **Consistent across all commands**: Time, Todo, TIL, Notes, Scratch all use tags the same way
- **Single-line/multi-line mode**: Tags extracted from the text itself
- **Editor mode** (`--edit`): Tags passed as CLI arguments, added to metadata line
- Tags stored on metadata line (separate from content)

### Tag Examples
```bash
# Time tracking with project tag
englog time start "Fix auth endpoints @api-refactor @backend @security"

# Multiple projects
englog time start "Update shared utils @api-refactor @mobile-app @refactor"

# No project (general tasks)
englog time start "Email responses @admin"

# Todo with project context
englog todo add "Review auth PR @api-refactor @code-review"

# TIL - single line
englog til "OAuth flow handles token refresh @api-refactor @security"

# TIL - editor mode with tags
englog til --edit @api-refactor @security
# Content in editor, tags in metadata from CLI args

# Note
englog note "API endpoint: https://api.example.com @api @reference"

# Scratch for quick debug dump
englog scratch --edit @error @debugging
```

## File Structure

### Directory Layout
```
$ENGLOG_DIR/                       # Default: ~/englog
├── 2025-01-15.md                  # Single daily file
├── 2025-01-16.md
└── 2025-01-17.md
```

### Daily File Format
```markdown
# 2025-01-15

## Time

### 09:23 - 10:46 | Fix auth endpoints | @api-refactor @backend @security
- Duration: 1h 23m

### 10:46 - 11:31 | Review security PR | @code-review @urgent
- Duration: 45m

### 13:00 - 15:10 | Fix auth endpoints | @api-refactor @backend @security
- Duration: 2h 10m

### 15:30 - [ACTIVE] | Debug memory leak | @bug-fixes @performance
- Duration: 1h 15m (running)

## Todo

### Todo
- [14:20] Update documentation @docs @api @api-refactor
- [15:30] Review PR #234 @code-review @api-refactor

### Doing
- [09:45] Fix authentication bug @backend @security @urgent @api-refactor

### Done
- [11:30] Deploy staging environment @devops @deployment @api-refactor
- [15:00] Write release notes @documentation @v2.0 @api-refactor

## TIL

### 10:15 | @python @performance
Python's `walrus operator` can simplify list comprehensions with filtering.

### 14:30 | @git @workflow
Git `--fixup` commits can auto-squash during interactive rebase.

## Notes

### 09:15 | @api @authentication @reference @api-refactor
API endpoint: https://api.example.com/v2/users
Auth token expires in 24h

### 10:45 | @team-update @reference
Sarah is now leading the mobile team. New sprint cadence starts next week.

### 14:00 | @deprecation @reference @api-refactor
Legacy auth service deprecated - migrate to OAuth2 by Q2. Impacts: login flow, API clients, mobile apps.

## Scratch

### 11:00 | @error @debugging @kubernetes
```
Error output from failed deployment...
```

### 15:30 | @temp @investigation
Quick debug trace - memory usage spike at 3PM
```

**File Structure Notes:**
- Sections created on first use (not all sections required)
- Daily file created automatically on first command of the day
- Sections always in order: Time → Todo → TIL → Notes → Scratch
- Each section uses H2 headers (`##`)
- Entries within sections use H3 headers (`###`)
- Active timer format: `START_TIME - [ACTIVE] | description | @tags`
- Completed timer format: `START_TIME - END_TIME | description | @tags`
- **Tags always on metadata line** (after `|`), separate from content
- **Todo entries removed from previous section when moved** (clean format, no strikethrough)
- **No task numbers stored in markdown** (numbers are display-only in `list` commands)
- **Time entries can repeat** (same task, multiple sessions, separate entries)

## Configuration

### Environment Variables

**`$ENGLOG_DIR`** (optional)
- Where daily markdown files are stored
- Default: `~/englog`
- Example: `export ENGLOG_DIR=~/Documents/englog`

**`$EDITOR`** (required for `--edit` and `englog edit`)
- Editor to use for multi-line input
- Standard environment variable
- Example: `export EDITOR=vim` or `export EDITOR=code --wait`

### File Formats (Fixed)

**Time format**: 24-hour format `HH:MM` (e.g., `13:15`, `09:23`)

**Date format**: ISO 8601 `YYYY-MM-DD` (e.g., `2025-01-15`)

**Timezone**: Local timezone for all timestamps

### No Config File

englog uses convention over configuration:
- No `.englogrc` or config file needed
- All settings via environment variables or fixed conventions
- Simpler to use, one less thing to manage

## Technical Stack

### Dependencies
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Package management
- [ruff](https://github.com/astral-sh/ruff) - Linting/formatting
- [typer](https://github.com/tiangolo/typer) - CLI framework
- [ty](https://github.com/astral-sh/ty) - Type checker and language server

### Project Structure
```
englog/
├── pyproject.toml
├── README.md
├── src/
│   └── englog/
│       ├── __init__.py
│       ├── cli.py           # Main CLI entry point
│       ├── commands/
│       │   ├── time.py      # Time tracking commands
│       │   ├── todo.py      # Todo commands (with matching logic)
│       │   ├── til.py       # TIL commands
│       │   ├── note.py      # Note commands
│       │   └── scratch.py   # Scratch commands
│       ├── core/
│       │   ├── config.py    # Environment variable handling
│       │   ├── file.py      # Daily file operations
│       │   ├── timer.py     # Timer state management
│       │   ├── tags.py      # Tag parsing/formatting
│       │   └── todo.py      # Todo matching and listing logic
│       └── utils/
│           └── formatting.py # Timestamp/formatting helpers
└── tests/
    ├── test_time.py
    ├── test_todo.py
    ├── test_til.py
    ├── test_note.py
    ├── test_scratch.py
    ├── test_tags.py
    └── test_file.py
```

**Core module details:**
```python
# src/englog/core/config.py
def get_englog_dir() -> Path:
    """Get englog directory from $ENGLOG_DIR or default to ~/englog"""

def get_editor() -> str:
    """Get editor from $EDITOR, raise error if not set"""

# src/englog/core/file.py
def get_daily_file_path(date: Optional[date] = None) -> Path:
    """Get path to daily file, defaults to today"""

def ensure_daily_file_exists(date: Optional[date] = None) -> Path:
    """Create daily file if it doesn't exist, return path"""

def append_to_section(section: str, content: str) -> None:
    """Append content to a section, create section if needed"""

# src/englog/core/timer.py
def get_active_timer() -> Optional[TimerEntry]:
    """Get currently active timer from today's file"""

def start_timer(description: str, tags: List[str]) -> None:
    """Start new timer, auto-stop active timer if exists"""

def stop_timer() -> TimerEntry:
    """Stop active timer and log duration"""

def pause_timer() -> None:
    """Pause active timer"""

def resume_timer() -> None:
    """Resume paused timer"""

def list_timers() -> List[TimerEntry]:
    """List all timers from today with numbers"""

def calculate_total_time() -> str:
    """Calculate total time tracked today (sum of all timer durations)"""

def find_timer_by_description(description: str) -> Optional[TimerEntry]:
    """Find most recent timer matching description (for restart)"""

def find_timer_by_number(number: int) -> Optional[TimerEntry]:
    """Find timer by list number (for restart)"""

# src/englog/core/todo.py
def find_todo_by_description(description: str, section: str) -> Optional[TodoEntry]:
    """
    Find todo by exact description match (case-insensitive)
    Matches on description only (ignores tags, timestamps)
    """

def find_todo_by_number(number: int) -> Optional[TodoEntry]:
    """
    Find todo by display number in Todo or Doing sections only
    Numbers are calculated dynamically from current file state
    Done items are not numbered and cannot be referenced by number
    """

def list_todos_with_numbers() -> str:
    """
    Generate numbered list output for Todo and Doing sections
    Done section shows items without numbers
    Returns formatted string with section headers and entries
    """

def move_todo(source_entry: TodoEntry, target_section: str) -> None:
    """
    Remove entry from source section, add to target section with new timestamp
    """
```

## Implementation Phases

### Phase 1 - MVP (v0.1.0)
**Core Functionality:**
- [ ] Project setup with uv
- [ ] Basic CLI structure with typer
- [ ] Environment variable handling ($ENGLOG_DIR, $EDITOR)
- [ ] `init` command - create englog directory
- [ ] Single daily file management (create/append to sections)
- [ ] Tag parsing and formatting (consistent across all commands)
- [ ] `note` command - single-line and multi-line notes with tags
- [ ] `til` command - single-line and multi-line TILs with tags
- [ ] `scratch` command - single-line and multi-line scratch with tags
- [ ] File creation with timestamps (local timezone, 24h format)
- [ ] `status` command - show active timer, total time today, and todo counts
- [ ] `edit` command - open today's file in editor
- [ ] `version` command - show version

**Testing & Quality:**
- [ ] Unit tests for core modules (file, tags, formatting)
- [ ] Integration tests for commands
- [ ] Error handling for all commands
- [ ] Test coverage for edge cases (empty files, missing $EDITOR, etc.)

### Phase 2 - Core Features (v0.2.0)
**Todo System:**
- [ ] `todo add` command with tags
- [ ] `todo list` command - display with dynamic numbers (Todo/Doing only)
- [ ] `todo doing/done` by description (exact match, case-insensitive)
- [ ] `todo doing/done` by number (search Todo/Doing only, not Done)
- [ ] Remove from previous section when moved
- [ ] Tests for todo matching logic

**Time Tracking:**
- [ ] `time start` command with tags and auto-stop
- [ ] `time start` by number (restart from list)
- [ ] `time start` by description (restart matching timer)
- [ ] Show "Stopped/Started" messages on timer switch
- [ ] `time pause/resume/stop` commands
- [ ] `time list` command - display all timers with numbers and total
- [ ] Timer state persistence in markdown (separate entries for restarts)
- [ ] Calculate total time tracked today
- [ ] Tests for timer state management and restart logic

**Multi-line Input:**
- [ ] `--edit` flag for til/note/scratch
- [ ] Tag handling for editor mode (CLI args → metadata)
- [ ] Multi-line paste support (without --edit)
- [ ] Tests for multi-line input modes

### Phase 3 - Polish & Release (v0.3.0)
- [ ] Comprehensive error messages
- [ ] Installation script with alias setup (`alias el='englog'`)
- [ ] README with examples and workflow guide
- [ ] Contributing guide
- [ ] Release documentation
- [ ] Performance optimization if needed

## Error Handling Summary

### Command Errors
- No active timer for `pause/resume/stop` → "No active timer"
- No paused timer for `resume` → "No paused timer to resume"
- Invalid todo number → "Task #X not found in Todo or Doing sections"
- Invalid timer number → "Timer #X not found"
- Missing `$EDITOR` for `--edit` or `englog edit` → "EDITOR environment variable not set"
- Empty content after `--edit` → Warning: "Empty content, entry not created"

### File System Errors
- Cannot create englog directory → "Cannot create directory: [path] ([reason])"
- Cannot write to daily file → "Cannot write to file: [path] ([reason])"
- Cannot read daily file → "Cannot read file: [path] ([reason])"
- Today's file doesn't exist for `englog edit` → Create with basic structure, then open

### Graceful Degradation
- Daily file doesn't exist → Create on first command
- Empty daily file → Create sections as needed
- Empty sections → Show appropriate messages in `status` ("No todos today", "Time Today: 0h 0m")
- `$ENGLOG_DIR` not set → Use `~/englog` default
- Directory already exists on `init` → Show friendly message, not error

### User-Friendly Error Messages
All errors should:
- Be clear and actionable
- Suggest fixes when possible (e.g., "Set $EDITOR: export EDITOR=vim")
- Use consistent formatting
- Avoid technical jargon where possible

## Resolved Questions

3. **Todo matching**: Hybrid approach with two methods
   - **By description**: Exact match (case-insensitive, tags can differ)
   - **By number**: Dynamic numbering for Todo and Doing only (Done items not numbered)
   - Remove from previous section when moved (clean format)
   - If no match found (description only), simply add new entry
   
6. **Tag placement in files**: Tags on separate metadata line (after `|`)

7. **Tag inheritance**: Tags parsed and stored in metadata for all commands (Time, Todo, TIL, Notes, Scratch)

8. **Timer auto-stop**: Show "Stopped: [task] (Xh Ym), Started: [new task]" message

9. **Empty status sections**: Show "No todos today" / "Time Today: 0h 0m" for empty sections

10. **File creation**: All commands create daily file automatically on first use

11. **Init behavior**: Only creates directory, no template or config files

12. **Version output**: `englog 0.1.0` format

13. **Multi-line input**: Works without flags (paste multiple lines)

14. **Timer restart**: Always creates new entry (separate sessions), not continuation

15. **Time tracking**: Option A - separate entries with future `englog time report` for totals

16. **Status total time**: Show total time tracked today (sum of all timer durations)

## Future Considerations (Post-v1.0)

- **`englog time report`** - Aggregate time by task/project/tag
  - Show total time per task across multiple sessions
  - Example: "Fix auth bug: 4h 48m (3 sessions)"
  - Filter by date range, tag, project
- `englog search` - Simple grep wrapper
- `englog export` - Export to JSON/CSV
- `englog list --tag @python` - Filter by tag across all entry types
- `englog tags` - List all used tags with counts
- `englog yesterday` / `englog open <date>` - View past days
- `englog show` - Display today's file in terminal
- `englog archive` - Archive old daily files
- Template support for custom formats
- Git integration (auto-commit daily files)
- Tag autocomplete from history
- Fuzzy matching for todos (if exact match proves too strict)
- `englog todo edit 3` - Edit todo by number
- `englog todo delete 5` - Delete todo by number
- `englog todo carry` - Copy unfinished todos to today
- Shell completions (bash, zsh, fish)

## End-of-Day Workflow

The tool is designed for a processing workflow:

1. **During the day**: Rapid capture with `englog` commands
```bash
   englog time start "Fix bug @backend"
   englog til "Use pytest fixtures for test setup @python @testing"
   englog note "New API endpoint deployed @api @reference"
   englog scratch "Error investigating: connection timeout"
   englog time list  # Review what you worked on
   englog status     # Quick overview with total time
```

2. **End of day**: Review your work
```bash
   englog status                      # Quick overview
   englog time list                   # See all work sessions with total
   englog todo list                   # Review todos
   englog edit                        # Open today's file for processing
```

3. **Process entries**: 
   - Extract completed todos to permanent task system
   - Move TILs to knowledge base organized by topic
   - Archive important notes/references to weekly notes
   - Discard scratch and temporary captures
   - Calculate total time spent on projects (sum duplicate tasks)
   - Review context switching patterns

4. **Optional**: Archive or delete processed daily file
```bash
   mv ~/englog/2025-01-15.md ~/englog/archive/
   # or
   rm ~/englog/2025-01-15.md
```

Daily files are ephemeral by design - they're optimized for capture speed, not permanent storage.

Tags provide consistent categorization across all entry types, making it easy to see all work related to a project or context.

The todo system allows flexible workflows:
- Quick capture: `englog todo done "Fix bug"` (matches or creates new)
- Explicit reference: `englog todo list` then `englog todo done 3` (when you want to be precise)
- Mixed approach: Use both methods as needed throughout the day

The time tracking system preserves your work timeline:
- Each restart creates a new entry showing exactly when you worked
- Use `englog time list` to see all sessions with total time
- Use `englog status` for quick overview of total time today
- Future `englog time report` will aggregate totals across sessions
- Honest representation of context switching

The separation of til/note/scratch provides semantic meaning during capture, helping you categorize information instinctively without thinking.

## Installation & Setup
```bash
# Install with uv
uv tool install englog

# Set up englog directory (optional, defaults to ~/englog)
export ENGLOG_DIR=~/Documents/englog

# Set up editor (required for --edit commands)
export EDITOR=vim  # or nano, code --wait, etc.

# Initialize
englog init

# Set up alias for even faster capture
echo 'alias el="englog"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc

# Start using
englog time start "First task @project"
englog til "Something I just learned @topic"
```

## Example Session
```bash
# Morning - start tracking time
$ englog time start "Review PRs @code-review"
Started: Review PRs

# Add some todos
$ englog todo add "Fix auth bug @backend @urgent"
$ englog todo add "Update docs @documentation"
$ englog todo add "Deploy to staging @devops"

# Switch tasks
$ englog time start "Fix auth bug @backend"
Stopped: Review PRs (45m), Started: Fix auth bug

# Mark todo as doing
$ englog todo doing "Fix auth bug"

# Capture a learning
$ englog til "Python dataclasses support frozen=True for immutability @python @tips"

# Quick note
$ englog note "New staging URL: https://staging.example.com @reference @devops"

# Complete the task
$ englog time stop
Stopped: Fix auth bug (2h 15m)

$ englog todo done "Fix auth bug"

# Need to come back to code review later
$ englog time list
1. Review PRs @code-review (45m)
2. Fix auth bug @backend (2h 15m)

Total: 3h 0m

# Restart code review by number
$ englog time start 1
Started: Review PRs @code-review

# Work for a while...
$ englog time stop
Stopped: Review PRs (1h 30m)

# Check overall status
$ englog status
Active Timer: None

Time Today: 4h 30m

Todos:
  Todo: 2 tasks
  Doing: 0 tasks
  Done: 1 task

# View all time entries (same task can appear multiple times)
$ englog time list
1. Review PRs @code-review (45m)
2. Fix auth bug @backend (2h 15m)
3. Review PRs @code-review (1h 30m)

Total: 4h 30m

# End of day - review everything
$ englog edit
```
