# Change: Improve Day One Importer

## Why
The current Day One importer has several issues that prevent proper formatting and functionality:
1. Newlines in note text are not properly rendered in Apple Notes
2. Day One exports contain markdown formatting that should be preserved since Apple Notes supports markdown
3. Tags from Day One entries are not being applied correctly in Apple Notes
4. No verification that Apple Notes is running before attempting import, leading to failures

These improvements will ensure imported notes maintain their original formatting, structure, and metadata.

## What Changes
- **MODIFIED**: Note text formatting to properly handle newlines (`\n`) so line breaks are preserved in Apple Notes
- **MODIFIED**: Note creation to preserve markdown formatting from Day One exports (Apple Notes supports markdown natively)
- **MODIFIED**: Tag application logic to correctly set tags in Apple Notes (fixing current implementation)
- **ADDED**: Pre-import check to verify Apple Notes application is running before attempting import

## Impact
- **Affected specs**: `dayone-import` capability
- **Affected code**: `dayone_import.py` - `NotesCreator` class, specifically text formatting, tag handling, and AppleScript execution
- **Dependencies**: None (uses existing AppleScript/osascript capabilities)
- **Breaking changes**: None (fixes existing functionality)
