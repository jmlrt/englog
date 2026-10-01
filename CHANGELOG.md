# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Breaking**: englog is now time tracking only. Daily files are `YYYY-MM-DD.txt` with one `HH:MM title` line per entry and `HH:MM stop` to end one. An entry ends at the next line and durations are computed, never stored. Existing `.md` files are not read.
- **Breaking**: commands are `englog start|stop|list|status|edit|version`, without the `time` subcommand. `start` takes the title unquoted and an optional `--at HH:MM` before it; `stop` takes `--at HH:MM` too.
- Reading a malformed file (bad time, missing title, out-of-order lines, dangling `stop`) fails with `file:line`.
- Durations print as `45m`, `1h`, `1h 5m`.

### Removed
- `todo`, `til`, `note` and `scratch` commands and their sections.
- Tags.
- `pause`, `resume` and restart-by-number.
- `init` (the directory is created on first write).
