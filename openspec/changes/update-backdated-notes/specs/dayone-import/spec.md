## MODIFIED Requirements

### Requirement: Date Preservation
The system SHALL attempt to preserve the original creation date from Day One entries in the Apple Notes by setting the note creation date when supported.

#### Scenario: Set note creation date
- **WHEN** an entry has a creationDate and Apple Notes accepts setting the creation date
- **THEN** the system sets the note creation date to match the entry's creationDate
- **AND** the note body remains unchanged

#### Scenario: Creation date setting fails
- **WHEN** an entry has a creationDate but Apple Notes rejects setting the creation date
- **THEN** the system appends the creation date to the note body or title as a fallback
- **AND** the system logs a warning about the fallback
