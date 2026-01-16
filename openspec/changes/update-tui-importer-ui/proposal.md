# Change: Update Day One Importer TUI

## Why
The current TUI feels dated and makes it harder to understand what will be imported, which entries are selected, and what settings will apply. A clearer, step-based flow with a markdown preview and a focused settings screen will make the import process faster and more confident without adding complexity, while keeping the interface fully textual.

## What Changes
- **ADDED**: Three-step textual TUI flow (Select Journals -> Settings -> Review/Import) with a progress indicator and sticky action bar
- **ADDED**: Markdown preview panel for the focused entry plus a lightweight multi-item preview
- **MODIFIED**: Journal selection UI to make multi-select easier (checkbox list with quick select/clear)
- **ADDED**: Simple settings screen for common options (folder, dry run, calendar stamp toggle, entry range selection)
- **MODIFIED**: End-of-run summary for both dry runs and actual imports

## Impact
- **Affected specs**: `dayone-import` capability
- **Affected code**: `dayone_import.py` (TUI flow, settings wiring, summary output)
- **Dependencies**: None (continue using Rich for TUI)
- **Breaking changes**: None (defaults preserve current behavior)
