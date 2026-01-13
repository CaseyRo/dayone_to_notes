# Day One to Apple Notes Import

A Python tool to import Day One journal entries into Apple Notes, preserving text content, images, videos, tags, and metadata.

## Features

- ✅ **Interactive TUI** - Beautiful text-based interface for file selection and progress tracking
- ✅ Parses Day One JSON exports (supports multiple JSON files)
- ✅ Imports text, photos, and videos
- ✅ Preserves Day One tags as Apple Notes tags
- ✅ Automatic folder creation (creates folder if it doesn't exist)
- ✅ Duplicate handling (creates numbered copies: "Note Title 2", "Note Title 3")
- ✅ Batch processing with real-time progress reporting
- ✅ Cancellable operations (Ctrl+C to cancel)
- ✅ Error handling and detailed logging

## Requirements

- macOS (uses AppleScript/osascript)
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager
- Apple Notes app
- Day One export in JSON format

## Quick Start

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd dayone_to_notes

# Sync dependencies (creates virtual environment)
uv sync

# Run the import
uv run dayone-import /path/to/dayone/export --folder "Day One Import"
```

## Installation

1. Clone or download this repository
2. Install UV if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Sync dependencies (creates virtual environment):
   ```bash
   uv sync
   ```
   
   Dependencies (managed by UV): `rich` for the TUI interface. UV will create a `.venv` directory automatically.

## Usage

All commands use `uv run` to execute in the project's virtual environment. You can use either:

- `uv run dayone_import.py` - Direct script execution
- `uv run dayone-import` - Installed command (recommended)

### Interactive TUI Mode (Default)

By default, the tool launches an interactive TUI that allows you to:

1. **Select JSON files** - Choose which journal files to import (if multiple exist)
2. **Choose folder** - Select or create the target Apple Notes folder
3. **Monitor progress** - See real-time progress with beautiful progress bars
4. **Cancel anytime** - Press Ctrl+C to cancel the import safely

```bash
uv run dayone-import /path/to/dayone/export
```

The TUI will:
- Show all available JSON files with checkboxes
- Allow you to toggle file selection by typing numbers (e.g., "1 3 5" to toggle files 1, 3, and 5)
- Display progress bars during parsing and importing
- Show verbose output when `--verbose` is used
- Provide a detailed summary at the end

### Classic Mode (No TUI)

Disable the TUI and use classic command-line mode:

```bash
uv run dayone-import /path/to/dayone/export --no-tui
```

### Basic Import

Import all entries from a Day One export to the default Notes folder:

```bash
uv run dayone-import /path/to/dayone/export
```

### Import to Specific Folder

Import to a named folder (folder will be created if it doesn't exist):

```bash
uv run dayone-import /path/to/dayone/export --folder "Day One Import"
```

### Dry Run

Test the import without actually creating notes:

```bash
uv run dayone-import /path/to/dayone/export --dry-run
```

### Verbose Output

Get detailed logging output:

```bash
uv run dayone-import /path/to/dayone/export --verbose
```

### Combined Options

```bash
uv run dayone-import /path/to/dayone/export --folder "My Journal" --verbose
```

### Cancelling an Import

You can cancel an import at any time by pressing **Ctrl+C**. The tool will:
- Finish the current entry being processed
- Display a summary of what was completed
- Exit gracefully

This is safe and won't corrupt any notes that were already created.

## Day One Export Format

The tool expects a Day One export directory with the following structure:

```
export_directory/
├── Journal.json          # One or more JSON files
├── Instagram.json         # All .json files are processed
├── Work daily.json        # Multiple journals are supported
├── photos/                # Photo files (shared across all journals)
└── videos/                # Video files (optional, shared across all journals)
```

**Multiple JSON Files**: The tool automatically processes ALL `.json` files found in the export directory. If you have multiple journals exported (e.g., "Journal.json", "Instagram.json", "Work daily.json"), they will all be imported in a single run.

To export from Day One:
1. Open Day One app
2. Go to File > Export > JSON
3. Choose a location and export
4. Use the exported directory path with this tool
5. All JSON files in that directory will be processed automatically

## Features Explained

### Folder Organization

- If you specify a folder with `--folder`, the tool will create it if it doesn't exist
- If no folder is specified, notes are created in the default Notes folder
- All imported notes are placed in the specified folder

### Duplicate Handling

If a note with the same title already exists, the tool creates numbered copies:
- First duplicate: "Note Title 2"
- Second duplicate: "Note Title 3"
- And so on...

This ensures no entries are lost during import.

### Tag Preservation

Day One tags are automatically applied as Apple Notes tags when possible. If tag application fails (e.g., on older macOS versions), the note is still created with all other content.

### Media Files

- Photos and videos are automatically attached to notes
- If a media file cannot be found, a warning is logged but processing continues
- Media files are matched by identifier or MD5 hash
- Missing media files are reported in the summary

## Command-Line Options

```
positional arguments:
  export_dir            Path to Day One export directory

optional arguments:
  -h, --help            Show help message
  -f FOLDER, --folder FOLDER
                        Target folder name in Apple Notes
  --dry-run            Test run without creating notes
  -v, --verbose         Enable verbose logging
  --no-tui              Disable TUI and use classic mode
```

## Troubleshooting

### "Notes app not running" or Permission Errors

- Make sure Apple Notes is open before running the import
- Grant Terminal/iTerm full disk access in System Preferences > Security & Privacy > Privacy > Full Disk Access

### "No JSON files found"

- Verify the export directory contains `.json` files
- Check that the path is correct and accessible

### Media Files Not Attached

- Ensure `photos/` and `videos/` directories exist in the export directory
- Check that media files are present and readable
- Use `--verbose` to see detailed error messages

### AppleScript Errors

- Ensure you're running on macOS (AppleScript is macOS-only)
- Check that Apple Notes is installed and accessible
- Try running with `--verbose` to see detailed error messages

## Limitations

- One-time import only (no synchronization)
- Audio attachments are not currently supported
- Creation date preservation depends on AppleScript capabilities (may fall back to including date in note content)
- Large exports may take significant time to process

## Examples

### Example 1: Simple Import

```bash
uv run dayone-import ~/Downloads/DayOneExport
```

### Example 2: Import to Specific Folder

```bash
uv run dayone-import ~/Downloads/DayOneExport --folder "My Day One Journal"
```

### Example 3: Test Import First

```bash
# Test without creating notes
uv run dayone-import ~/Downloads/DayOneExport --dry-run --folder "Test"

# If successful, run for real
uv run dayone-import ~/Downloads/DayOneExport --folder "My Journal"
```

## License

This project is provided as-is for personal use.
