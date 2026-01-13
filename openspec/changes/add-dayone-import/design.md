# Design: Day One to Apple Notes Import

## Context
Day One exports journal entries as JSON files with separate directories for photos and videos. Each entry contains:
- Text content (may include markdown-style image references)
- Arrays of photo/video objects with identifiers
- Creation dates, UUIDs, and optional tags
- Media files stored separately in `photos/` and `videos/` directories

Apple Notes can be automated via AppleScript to create notes, add attachments, and organize into folders.

## Goals / Non-Goals

### Goals
- Parse Day One JSON exports accurately
- Create Apple Notes with text content preserved
- Attach multiple images and videos per note
- Organize notes in a specific folder or with tags
- Preserve creation dates when possible
- Handle large batch imports efficiently
- Provide clear error reporting

### Non-Goals
- Real-time synchronization (one-time import only)
- Two-way sync between Day One and Notes
- Preserving Day One-specific formatting beyond basic text
- Handling audio attachments (out of scope for initial version)

## Decisions

### Decision: Use Python + osascript instead of pure AppleScript
**Rationale**: 
- Python provides better JSON parsing, file handling, and error management
- Easier to test and debug than pure AppleScript
- Can handle large batches with progress reporting
- More maintainable codebase

**Alternatives considered**:
- Pure AppleScript: Harder to debug, limited JSON parsing capabilities
- Siri Shortcuts: Requires manual shortcut creation, not suitable for automation
- Python + py-applescript library: Adds dependency, osascript is built-in

### Decision: Use osascript command-line tool
**Rationale**:
- Built into macOS, no additional dependencies
- Can execute AppleScript from Python subprocess
- Supports passing parameters to scripts
- Reliable and well-documented

**Alternatives considered**:
- py-applescript library: Additional dependency, may have compatibility issues
- Direct AppleScript files: Less flexible for dynamic content

### Decision: Organize by folder (with tag option)
**Rationale**:
- Folders provide clear visual separation in Notes app
- Tags can be added as secondary organization
- User can specify folder name during import
- Script will create the folder if it doesn't exist

**Alternatives considered**:
- Tags only: Less visible organization, harder to browse
- Both folder and tags: More complex, folder is sufficient for primary organization

### Decision: Create target folder if it doesn't exist
**Rationale**:
- Simplifies user workflow - no need to pre-create folders
- Reduces errors from missing folders
- Provides better user experience

**Alternatives considered**:
- Require folder to exist: Adds friction, requires manual setup

### Decision: Handle duplicates by creating numbered copies
**Rationale**:
- Preserves all entries even if UUIDs match
- Clear indication of duplicates with numbering (e.g., "Note Title 2")
- Prevents accidental data loss from skipping entries

**Alternatives considered**:
- Skip duplicates: Risk of losing data if entries were modified
- Update existing: Complex to determine what "update" means, risk of overwriting

### Decision: Preserve Day One tags as Apple Notes tags
**Rationale**:
- Maintains organization and searchability from Day One
- Apple Notes tags provide additional organization beyond folders
- Tags are searchable and filterable in Notes app

**Alternatives considered**:
- Folder only: Loses tag-based organization from Day One
- Ignore tags: Reduces functionality and organization options

### Decision: Map media files by identifier/MD5
**Rationale**:
- Day One uses identifiers in JSON that may not match filenames
- MD5 hashes provide reliable file matching
- Need to search photos/videos directories to find matching files
- Handle cases where media files are missing gracefully

**Alternatives considered**:
- Assume filename matches identifier: Not reliable based on export structure
- Use only MD5: Slower, identifier is faster primary lookup

## Risks / Trade-offs

### Risk: AppleScript limitations with large attachments
**Mitigation**: Test with various file sizes, add progress indicators, batch in smaller chunks if needed

### Risk: Notes app may not preserve exact creation dates
**Mitigation**: Add creation date as text in note if AppleScript doesn't support date setting, or use note title with date

### Risk: Media file resolution may be slow for large exports
**Mitigation**: Build index of media files at start, use efficient lookup (dictionary/hash map)

### Risk: AppleScript errors are hard to debug
**Mitigation**: Comprehensive error logging, test with small batches first, provide clear error messages

## Migration Plan
1. User exports Day One journal to JSON format
2. User runs import script with path to export directory
3. Script parses JSON, resolves media files, creates notes
4. Progress reported to console
5. Summary report of successes/failures
