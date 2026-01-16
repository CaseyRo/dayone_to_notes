# Change: Backdate Apple Notes entries using Day One creation dates

## Why
Day One exports include creation dates, but imported Notes entries currently use the current timestamp. Users expect imported notes to be backdated to match the original journal entry.

## What Changes
- **MODIFIED**: AppleScript note creation to set the note creation date to the Day One `creationDate` when available
- **ADDED**: Fallback behavior to append the original date into the note body or title when Apple Notes rejects date-setting

## Impact
- **Affected specs**: `dayone-import` capability (Date Preservation requirement)
- **Affected code**: `dayone_import.py` (NotesCreator date handling), `tests/test_notes_creator.py`, `README.md`
- **Breaking changes**: None
