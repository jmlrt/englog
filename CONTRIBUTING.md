# Contributing to englog

Thank you for your interest in contributing to englog!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/jmlrt/englog.git
cd englog

# Install dependencies (including dev dependencies)
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Project Structure

```
englog/
├── src/englog/
│   ├── cli.py              # Main CLI entry point
│   ├── commands/           # CLI command implementations
│   │   ├── time.py         # englog time start/stop/pause/resume/list
│   │   ├── todo.py         # englog todo add/doing/done/list
│   │   ├── til.py          # englog til
│   │   ├── note.py         # englog note
│   │   └── scratch.py      # englog scratch
│   ├── core/               # Business logic
│   │   ├── config.py       # Environment variable handling
│   │   ├── file.py         # Daily file operations
│   │   ├── timer.py        # Timer state management
│   │   ├── tags.py         # Tag parsing (@tagname format)
│   │   └── todo.py         # Todo matching/listing logic
│   └── utils/
│       └── formatting.py   # Timestamp/duration formatting
└── tests/
    ├── conftest.py         # Shared test fixtures
    ├── test_config.py
    ├── test_file.py
    ├── test_formatting.py
    ├── test_tags.py
    ├── test_timer.py
    └── test_todo.py
```

## Code Style

- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Follow existing code patterns
- Write tests for new functionality
- Keep functions focused and small

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_timer.py

# Run specific test
uv run pytest tests/test_timer.py::TestStartTimer::test_starts_new_timer
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run ruff check src/ tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Design Principles

When contributing, keep these principles in mind:

1. **Fast capture**: Commands should be quick to type and execute
2. **Markdown-first**: Output should be human-readable markdown
3. **Convention over configuration**: Minimize config options, use sensible defaults
4. **Ephemeral by design**: Daily files are meant to be processed and discarded

## Adding New Commands

1. Create a new file in `src/englog/commands/`
2. Register in `src/englog/cli.py`
3. Add tests in `tests/`
4. Update documentation

## Questions?

Open an issue for questions or discussions about potential changes.
