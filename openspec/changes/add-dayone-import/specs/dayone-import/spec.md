## ADDED Requirements

### Requirement: Day One JSON Export Parsing
The system SHALL parse Day One JSON export files to extract journal entries, including text content, photos, videos, creation dates, and metadata.

#### Scenario: Parse valid Day One export
- **WHEN** a valid Day One JSON export file is provided
- **THEN** the system extracts all entries from the `entries` array
- **AND** each entry's text, photos array, videos array, creationDate, uuid, and optional tags are parsed correctly

#### Scenario: Handle missing or malformed JSON
- **WHEN** the JSON file is missing, malformed, or invalid
- **THEN** the system reports a clear error message
- **AND** processing stops with appropriate error code

### Requirement: Media File Resolution
The system SHALL locate and map media files (photos and videos) referenced in Day One entries to actual files in the export directory.

#### Scenario: Resolve photo by identifier
- **WHEN** an entry contains a photo with an identifier
- **THEN** the system searches the `photos/` directory for a matching file
- **AND** matches by identifier (in filename or metadata) or MD5 hash
- **AND** returns the full path to the media file

#### Scenario: Resolve video by identifier
- **WHEN** an entry contains a video with an identifier
- **THEN** the system searches the `videos/` directory for a matching file
- **AND** matches by identifier or MD5 hash
- **AND** returns the full path to the media file

#### Scenario: Handle missing media files
- **WHEN** a referenced photo or video file cannot be found
- **THEN** the system logs a warning
- **AND** continues processing the entry without the missing media
- **AND** includes the missing media in the error report

### Requirement: Apple Notes Creation
The system SHALL create new notes in Apple Notes using AppleScript, including text content and media attachments.

#### Scenario: Create note with text only
- **WHEN** an entry has text content but no media
- **THEN** the system creates a new note in the specified folder
- **AND** the note contains the entry's text content
- **AND** the note is successfully created in Apple Notes

#### Scenario: Create note with text and images
- **WHEN** an entry has text and one or more photos
- **THEN** the system creates a new note with the text content
- **AND** all resolved photo files are attached to the note
- **AND** photos appear in the correct order as specified in the entry

#### Scenario: Create note with text and videos
- **WHEN** an entry has text and one or more videos
- **THEN** the system creates a new note with the text content
- **AND** all resolved video files are attached to the note
- **AND** videos appear in the correct order

#### Scenario: Create note with text, images, and videos
- **WHEN** an entry has text, photos, and videos
- **THEN** the system creates a new note with all content
- **AND** all media files are attached in the correct order (photos first, then videos, or by orderInEntry)

### Requirement: Folder Organization
The system SHALL organize imported notes into a specified Apple Notes folder, creating the folder if it doesn't exist.

#### Scenario: Create notes in specified folder
- **WHEN** a target folder name is provided
- **THEN** the system creates the folder if it doesn't exist
- **AND** creates all notes in that folder
- **AND** all imported notes are placed in that folder

#### Scenario: Fallback to default folder
- **WHEN** no folder is specified or the specified folder cannot be created
- **THEN** the system creates notes in the default Notes folder
- **AND** logs a warning about the folder issue

### Requirement: Date Preservation
The system SHALL attempt to preserve the original creation date from Day One entries in the Apple Notes.

#### Scenario: Set note creation date
- **WHEN** an entry has a creationDate
- **THEN** the system attempts to set the note's creation date to match
- **AND** if date setting is not supported, includes the date in the note title or content

### Requirement: Duplicate Entry Handling
The system SHALL handle duplicate entries by creating numbered copies when a note with the same content or identifier already exists.

#### Scenario: Create duplicate with number suffix
- **WHEN** an entry would create a note that already exists (same title/content)
- **THEN** the system creates a new note with a number suffix (e.g., "Note Title 2", "Note Title 3")
- **AND** continues processing without error
- **AND** includes duplicate count in the summary report

### Requirement: Tag Preservation
The system SHALL preserve Day One tags as Apple Notes tags when possible.

#### Scenario: Apply Day One tags to Apple Notes
- **WHEN** an entry contains tags in the Day One export
- **THEN** the system applies those tags to the created Apple Note
- **AND** if tag application fails, logs a warning but continues processing
- **AND** the note is still created with text and media even if tagging fails

### Requirement: Batch Processing
The system SHALL process multiple entries efficiently, providing progress feedback and error reporting.

#### Scenario: Process multiple entries
- **WHEN** a Day One export contains multiple entries
- **THEN** the system processes each entry sequentially
- **AND** displays progress (e.g., "Processing entry 5 of 100")
- **AND** continues processing even if individual entries fail

#### Scenario: Generate import summary
- **WHEN** batch processing completes
- **THEN** the system reports the total number of entries processed
- **AND** reports the number of successful imports
- **AND** reports the number of failures with details
- **AND** lists any missing media files

### Requirement: Error Handling and Logging
The system SHALL handle errors gracefully and provide clear logging for debugging and user feedback.

#### Scenario: Handle AppleScript errors
- **WHEN** AppleScript execution fails (e.g., Notes app not running, permission denied)
- **THEN** the system logs a clear error message
- **AND** continues processing remaining entries if possible
- **AND** includes the error in the final summary

#### Scenario: Handle file access errors
- **WHEN** media files cannot be accessed (permissions, missing files)
- **THEN** the system logs a warning
- **AND** continues processing without the affected media
- **AND** includes details in the error report
