# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Day One to Apple Notes Import Tool - A macOS Python CLI for importing Day One journal entries into Apple Notes, preserving text, images, videos, tags, and metadata. Uses AppleScript via `osascript` for Notes integration.

## Development Commands

```bash
# Install dependencies and set up environment
uv sync --all-extras

# Run tests
uv run pytest -v

# Run a single test file
uv run pytest tests/test_markdown.py -v

# Run the tool (interactive TUI mode)
uv run dayone-import /path/to/dayone/export

# Limit imports for testing (e.g., first 5 entries)
uv run dayone-import /path/to/dayone/export --limit 5

# Dry run without creating notes
uv run dayone-import /path/to/dayone/export --dry-run

# Verbose output for debugging
uv run dayone-import /path/to/dayone/export --verbose

# Classic mode (no TUI)
uv run dayone-import /path/to/dayone/export --no-tui
```

## Architecture

Single-file implementation (`dayone_import.py`) with five main classes:

- **DayOneParser**: Parses Day One JSON exports, extracts entries with uuid, text, creationDate, photos, videos, and tags
- **MediaResolver**: Indexes and resolves media files from `photos/` and `videos/` directories by identifier or MD5 hash
- **MarkdownConverter**: Converts Day One markdown to HTML for Apple Notes (Notes body accepts HTML, not raw markdown)
- **NotesCreator**: Creates notes in Apple Notes via AppleScript, handles folder creation, duplicate titles, and tag insertion as hashtags
- **DayOneImporter**: Orchestrates the import process, supports both TUI (rich library) and classic console modes

## Key Implementation Details

- **Markdown to HTML**: Apple Notes body property accepts HTML. Raw markdown displays as plain text. MarkdownConverter converts headers, bold, italic, and lists to HTML tags.
- Day One image refs (`![](dayone-moment://...)`) are stripped from text - media handled separately as attachments
- AppleScript strings require escaping backslashes and quotes (`_escape_applescript_string`)
- Tags are added as hashtags appended to note body (most reliable across macOS versions)
- Media attachments are added via AppleScript `make new attachment` with POSIX file paths
- Duplicate note titles get numbered suffixes: "Title 2", "Title 3", etc.
- TUI is optional - falls back gracefully if `rich` is not available

## Dependencies

- Python 3.7+
- `rich` - TUI interface (progress bars, tables, prompts)
- `markdown` - Converts markdown to HTML for Apple Notes
- `pytest` (dev) - Testing framework
- macOS required (uses `osascript` for AppleScript execution)

## OpenSpec

This project uses OpenSpec for spec-driven development. When making changes that involve new features, breaking changes, or architecture shifts, open `openspec/AGENTS.md` for instructions on creating change proposals.
