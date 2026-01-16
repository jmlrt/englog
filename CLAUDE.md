# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

englog is a minimalist CLI tool for software engineers to capture workday data as timestamped markdown files. Core philosophy: fast capture, markdown-first, processing elsewhere.

## Build & Development Commands

Use the Makefile for all common operations:

```bash
make help       # Show all available commands
make install    # Install dependencies + pre-commit hooks
make test       # Run tests (quick)
make test-cov   # Run tests with coverage
make lint       # Run linter
make format     # Format code
make fix        # Auto-fix lint issues
make typecheck  # Run type checker (ty)
make pre-commit # Run all pre-commit hooks
make check      # Run lint + typecheck + tests (use before commits)
make clean      # Remove build artifacts
```

For specific test runs:
```bash
uv run pytest tests/test_timer.py   # Single file
uv run pytest -k "test_start"       # Pattern match
```

## CI/CD

GitHub Actions runs on all PRs to `main`:
- Linting (ruff check)
- Formatting (ruff format --check)
- Type checking (ty)
- Tests (pytest) on Python 3.12, 3.13, 3.14

Pre-commit hooks run automatically on `git commit`:
- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML validation
- Ruff linting and formatting

## Architecture

### Project Structure
```
src/englog/
├── cli.py              # Main CLI entry point (typer app)
├── commands/           # CLI command implementations
│   ├── entry.py        # Shared logic for til/note/scratch (factory pattern)
│   ├── time.py         # englog time start/stop/pause/resume/list
│   ├── todo.py         # englog todo add/doing/done/list
│   ├── til.py          # englog til (uses entry.py)
│   ├── note.py         # englog note (uses entry.py)
│   └── scratch.py      # englog scratch (uses entry.py)
├── core/               # Business logic
│   ├── config.py       # $ENGLOG_DIR, $EDITOR handling
│   ├── file.py         # Daily file operations
│   ├── timer.py        # Timer state management
│   ├── tags.py         # Tag parsing (@tagname format)
│   └── todo.py         # Todo matching/listing logic
└── utils/
    └── formatting.py   # Timestamp/duration/pluralization helpers
```

### Key Design Patterns

1. **Single daily file**: All data stored in `$ENGLOG_DIR/YYYY-MM-DD.md`
2. **Section-based markdown**: Time → Todo → TIL → Notes → Scratch (H2 headers)
3. **Tags everywhere**: `@tagname` format, parsed from text or CLI args
4. **Timer restarts create new entries**: Each `englog time start` creates separate entry, preserving timeline
5. **Todo matching**: By description (exact, case-insensitive) or by number (from `englog todo list`)
6. **Convention over configuration**: Only env vars ($ENGLOG_DIR, $EDITOR), no config files

### Markdown File Format

```markdown
# 2025-01-15

## Time
### 09:23 - 10:46 | Task description | @tag1 @tag2
- Duration: 1h 23m

## Todo
### Todo
- [14:20] Task description @tag1
### Doing
- [09:45] Task description @tag2
### Done
- [11:30] Task description @tag3

## TIL
### 10:15 | @tag1 @tag2
Content here.

## Notes
### 09:15 | @tag1
Content here.

## Scratch
### 11:00 | @tag1
Content here.
```

## Implementation Notes

- CLI framework: typer
- Active timer marked with `[ACTIVE]` in markdown
- Paused timer marked with `[PAUSED]` in markdown
- Todo numbers are display-only (not stored in file)
- Done items cannot transition (not numbered in list)
- `--edit` flag opens $EDITOR for multi-line input via tempfile

## Adding New Commands

### For entry-style commands (til, note, scratch pattern):

Use the factory in `entry.py`:

1. Create `src/englog/commands/newcmd.py`:
```python
from englog.commands.entry import create_entry_command

newcmd_command = create_entry_command("SectionName", "DisplayName")
newcmd_command.__doc__ = "Description for --help."
```

2. Register in `src/englog/cli.py`:
```python
from englog.commands import newcmd
app.command(name="newcmd")(newcmd.newcmd_command)
```

### For subcommand groups (time, todo pattern):

1. Create command file with typer subapp:
```python
import typer
app = typer.Typer()

@app.command()
def subcommand():
    pass
```

2. Register in cli.py:
```python
from englog.commands import newgroup
app.add_typer(newgroup.app, name="newgroup")
```

**IMPORTANT**: Always use `name=` parameter with `app.command()` to avoid "-command" suffix in CLI help.

## Test Strategy

### Test Layers

1. **Unit tests for core modules** (`test_<module>.py`)
   - Test business logic in isolation
   - Located in `tests/test_config.py`, `test_file.py`, `test_tags.py`, `test_timer.py`, `test_todo.py`, `test_formatting.py`
   - High coverage target (95%+)

2. **Unit tests for CLI commands** (`test_cli_<group>.py`)
   - Test CLI-specific behavior ONLY: exit codes, output messages, argument handling
   - Do NOT re-test core logic already covered by core tests
   - Located in `tests/test_cli_time.py`, `test_cli_todo.py`, `test_cli_entry.py`, `test_cli_utils.py`
   - Focus on error cases and user-facing messages

3. **Integration tests** (`test_integration.py`)
   - Test critical end-to-end workflows that span multiple commands
   - Verify file output matches expected markdown format
   - Keep minimal - only test what unit tests can't cover

### What Each Layer Tests

| Layer | Tests | Does NOT Test |
|-------|-------|---------------|
| Core unit | Timer state, todo matching, file operations, tag parsing | CLI output, exit codes |
| CLI unit | Exit codes, error messages, argument validation | Business logic, file content |
| Integration | Multi-command workflows, file format correctness | Edge cases (covered by unit tests) |

### Test Fixtures (conftest.py)
- `temp_englog_dir`: Creates isolated temp directory, sets ENGLOG_DIR
- `mock_editor`: Sets EDITOR to `cat` (no-op)
- `no_editor`: Removes EDITOR env var

### Running Tests
```bash
make test                           # Quick summary
make test-cov                       # With coverage
uv run pytest tests/test_timer.py   # Single file
uv run pytest -k "test_start"       # Pattern match
```

## Key Regex Patterns

### Tag parsing (core/tags.py):
```python
TAG_PATTERN = re.compile(r"@([a-zA-Z0-9_-]+)")
```

### Timer entry parsing (core/timer.py):
```python
# Active: ### 09:23 - [ACTIVE] | Description | @tag
# Completed: ### 09:23 - 10:45 | Description | @tag
TIMER_PATTERN = re.compile(
    r"^### (\d{2}:\d{2}) - (\[ACTIVE\]|\[PAUSED\]|\d{2}:\d{2}) \| (.+?) \| (.*)$"
)
```

### Todo entry parsing (core/todo.py):
```python
# Format: - [14:20] Task description @tag1 @tag2
TODO_PATTERN = re.compile(r"^- \[(\d{2}:\d{2})\] (.+)$")
```

## Common Issues and Fixes

### "command-name" suffix in CLI help
**Problem**: Command shows as `til-command` instead of `til`
**Fix**: Use explicit name parameter:
```python
# Wrong
app.command()(til.til_command)
# Correct
app.command(name="til")(til.til_command)
```

### Import errors (F401)
**Fix**: Run `uv run ruff check --fix src/ tests/` to auto-remove unused imports

### Import sorting (I001)
**Fix**: Run `uv run ruff check --fix src/ tests/` to auto-sort imports

### Line too long (E501)
**Note**: E501 is ignored in ruff config (pyproject.toml) - line-length is 100

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENGLOG_DIR` | No | `~/englog` | Directory for daily files |
| `EDITOR` | For --edit | None | Editor command (vim, nano, code --wait) |

## Section Ordering

Sections in daily file are always in this order (defined in core/file.py):
```python
SECTIONS = ["Time", "Todo", "TIL", "Notes", "Scratch"]
```

When appending to a section, the code ensures sections are created in order if they don't exist.

## Code Style Guidelines

### Modern Python (3.11+)
- Use `X | None` instead of `Optional[X]`
- Use `list[str]` instead of `List[str]`
- Use `dict[str, int]` instead of `Dict[str, int]`

### Pythonic idioms
- Use `next((x for x in items if condition), None)` instead of for-loop-with-return
- Use `divmod(a, b)` instead of `a // b` and `a % b`
- Use `all()`, `any()` for boolean checks on iterables

### DRY and KISS
- Extract shared logic into helper functions (see `_move_to_section` in todo.py)
- Use factory functions for similar commands (see `create_entry_command` in entry.py)
- Use `formatting.pluralize()` for count-based strings

### Imports
- All imports at top of file (no local imports inside functions)
- Group: stdlib → third-party → local
- Let ruff auto-sort with `ruff check --fix`
