# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

englog is a minimalist CLI that logs a workday as time entries in a plain text file (one `HH:MM title` line per entry,
`HH:MM stop` ends one). Durations are computed, never stored. See `SPEC.md` for the format and command behavior.

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
uv run pytest tests/test_log.py     # Single file
uv run pytest -k "test_start"       # Pattern match
```

## CI/CD

GitHub Actions runs on all PRs to `main`:
- Linting (ruff check)
- Formatting (ruff format --check)
- Type checking (ty)
- Tests (pytest) on Python 3.12, 3.13, 3.14

Pre-commit hooks run automatically on `git commit`: whitespace and end-of-file fixers, YAML/TOML validation, ruff
linting and formatting.

## Architecture

```
src/englog/
├── cli.py              # Typer app: start, stop, list, status, edit, version
├── core/
│   ├── config.py       # $ENGLOG_DIR, $EDITOR handling
│   └── log.py          # Parsing, validation, entries, start/stop (pure functions, `now` is a parameter)
└── utils/
    └── formatting.py   # format_duration
```

### Key Design Patterns

1. **One file per day**: `$ENGLOG_DIR/YYYY-MM-DD.txt`
2. **Nothing derived is stored**: an entry ends at the next line, durations are computed on read
3. **Fail fast**: reading a malformed file raises `ValueError` with `file:line`; the CLI turns it into `Error: ...`
   and exit code 1. Writes validate before touching the file.
4. **Time is a parameter**: `core/log.py` never calls the clock, `cli._now()` does, so tests pin it by patching
   `englog.cli._now`
5. **Convention over configuration**: only `$ENGLOG_DIR` and `$EDITOR`, no config files

## Implementation Notes

- CLI framework: typer
- `start` uses `context_settings={"allow_interspersed_args": False}` so `--at` is only parsed before the title and the
  rest is the title (no quoting needed)
- Always use `name=` with `app.command()` when the function name differs from the command (e.g. `list_cmd` → `list`)

## Test Strategy

1. **Core** (`tests/test_log.py`, `test_config.py`, `test_formatting.py`): parsing, validation, entries, start/stop
   against a temp directory.
2. **CLI** (`tests/test_cli.py`): exit codes, output messages, argument handling. Don't re-test core logic.

Fixtures (`conftest.py`): `temp_englog_dir` (isolated dir, sets `ENGLOG_DIR`), `mock_editor` (EDITOR=`cat`),
`no_editor`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENGLOG_DIR` | No | `~/englog` | Directory for daily files |
| `EDITOR` | For `edit` | None | Editor command |

## Code Style Guidelines

### Modern Python (3.12+)
- Use `X | None` instead of `Optional[X]`
- Use `list[str]` instead of `List[str]`

### Pythonic idioms
- Use `divmod(a, b)` instead of `a // b` and `a % b`
- Use `all()`, `any()` for boolean checks on iterables

### Imports
- All imports at top of file (no local imports inside functions)
- Group: stdlib → third-party → local
- Let ruff auto-sort with `ruff check --fix`

## Development Practices

When fixing a bug or inconsistency in one CLI command, proactively check ALL similar commands for the same issue before
considering the task done. Do not wait for the user to ask twice.

## Git Workflow

When staging and committing changes, ensure ONLY changes from the current task are included. Review staged files against
the current session scope before committing.
