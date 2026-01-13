## MODIFIED Requirements

### Requirement: Apple Notes Creation
The system SHALL create new notes in Apple Notes using AppleScript, including text content with proper formatting and media attachments.

#### Scenario: Create note with text only
- **WHEN** an entry has text content but no media
- **THEN** the system creates a new note in the specified folder
- **AND** the note contains the entry's text content with newlines properly preserved
- **AND** markdown formatting in the text is preserved (Apple Notes supports markdown natively)
- **AND** the note is successfully created in Apple Notes

#### Scenario: Create note with text and images
- **WHEN** an entry has text and one or more photos
- **THEN** the system creates a new note with the text content
- **AND** newlines in the text are rendered as line breaks
- **AND** markdown formatting is preserved in the note body
- **AND** all resolved photo files are attached to the note
- **AND** photos appear in the correct order as specified in the entry

#### Scenario: Create note with text and videos
- **WHEN** an entry has text and one or more videos
- **THEN** the system creates a new note with the text content
- **AND** newlines in the text are rendered as line breaks
- **AND** markdown formatting is preserved in the note body
- **AND** all resolved video files are attached to the note
- **AND** videos appear in the correct order

#### Scenario: Create note with text, images, and videos
- **WHEN** an entry has text, photos, and videos
- **THEN** the system creates a new note with all content
- **AND** newlines and markdown formatting in text are preserved
- **AND** all media files are attached in the correct order (photos first, then videos, or by orderInEntry)

### Requirement: Tag Preservation
The system SHALL preserve Day One tags as Apple Notes tags, ensuring they are correctly applied and visible in the Notes interface.

#### Scenario: Apply Day One tags to Apple Notes
- **WHEN** an entry contains tags in the Day One export
- **THEN** the system applies those tags to the created Apple Note using the correct AppleScript method
- **AND** tags are visible and functional in the Apple Notes interface
- **AND** if tag application fails, logs a warning but continues processing
- **AND** the note is still created with text and media even if tagging fails

#### Scenario: Apply multiple tags
- **WHEN** an entry contains multiple tags
- **THEN** all tags are applied to the note
- **AND** all tags are visible and functional in Apple Notes
- **AND** tags can be used for filtering/searching in Apple Notes

## ADDED Requirements

### Requirement: Pre-Import Validation
The system SHALL verify that Apple Notes is running before attempting to import entries.

#### Scenario: Check Notes app is running
- **WHEN** import process is initiated
- **THEN** the system checks if Apple Notes application is running
- **AND** if Notes is not running, displays a clear error message and stops processing
- **AND** if Notes is running, proceeds with import

#### Scenario: Handle Notes app not running
- **WHEN** Apple Notes is not running when import is attempted
- **THEN** the system reports an error indicating Notes must be running
- **AND** provides guidance on how to open Notes app
- **AND** exits with appropriate error code without creating any notes
