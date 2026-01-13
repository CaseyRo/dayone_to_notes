# Change: Add Day One to Apple Notes Import

## Why
The user wants to migrate their Day One journal entries into Apple Notes, preserving text content, images, videos, and metadata. The current project mentions using shortcuts, but a more robust solution is needed that can handle batch imports, media attachments, and proper organization.

## What Changes
- **ADDED**: Day One JSON export parser that extracts entries, text, photos, and videos
- **ADDED**: Apple Notes integration using AppleScript/osascript to create notes with attachments
- **ADDED**: Media file resolution that maps Day One identifiers to actual files in photos/videos directories
- **ADDED**: Automatic folder creation - target folder is created if it doesn't exist
- **ADDED**: Duplicate handling - creates numbered copies (e.g., "Note Title 2") when duplicates are detected
- **ADDED**: Tag preservation - Day One tags are applied as Apple Notes tags when possible
- **ADDED**: Date preservation to maintain original creation dates in notes
- **ADDED**: Batch processing capability to handle large exports efficiently
- **ADDED**: Error handling and logging for failed imports

## Impact
- **Affected specs**: New capability `dayone-import`
- **Affected code**: New Python script(s) for parsing and importing
- **Dependencies**: Python 3.x, macOS Notes.app, AppleScript/osascript support
- **Breaking changes**: None (new functionality)
