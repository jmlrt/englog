# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-normalize quotes in command documentation: Double quotes within backticks are automatically converted to single quotes for safety. This prevents shell interpretation issues when copying commands from englog entries.

### Fixed
- Parser no longer silently drops timer entries missing trailing space after tags pipe (`|`). The regex pattern now correctly handles entries like `### 11:30 - 12:00 | Task |@tag` without a space between the pipe and tags field.
