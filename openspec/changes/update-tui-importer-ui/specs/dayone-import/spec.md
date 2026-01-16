## ADDED Requirements

### Requirement: Step-Based TUI Flow
The system SHALL present a three-step textual TUI flow: Select Journals, Settings, and Review/Import.

#### Scenario: Start at journal selection
- **WHEN** the user launches the importer in TUI mode
- **THEN** the Select Journals step is shown first
- **AND** a progress indicator shows all three steps
- **AND** a sticky action bar shows the available actions for the current step

#### Scenario: Block progress when no journals selected
- **WHEN** no journals are selected in the Select Journals step
- **THEN** the system disables proceeding to the next step
- **AND** provides a clear prompt to select at least one journal

### Requirement: Journal Selection Controls
The system SHALL provide simple multi-select controls for choosing one or more journals to import.

#### Scenario: Multi-select with quick actions
- **WHEN** the user is in the Select Journals step
- **THEN** the system displays a checkbox list of available journals
- **AND** supports select all and clear selection actions
- **AND** shows a count of selected journals

### Requirement: Markdown Preview
The system SHALL display a markdown preview of the focused entry and provide a lightweight multi-item preview.

#### Scenario: Focused entry preview
- **WHEN** the user focuses an entry in the Review/Import step
- **THEN** the system shows a markdown preview of that entry

#### Scenario: Multi-item preview
- **WHEN** the user is in the Review/Import step
- **THEN** the system shows a small preview list of multiple entries
- **AND** indicates which entry is currently focused

### Requirement: Settings Screen
The system SHALL provide a settings screen for common import options without adding unnecessary complexity.

#### Scenario: Configure settings
- **WHEN** the user enters the Settings step
- **THEN** the system offers controls for target folder, dry run, calendar stamp toggle, and entry range selection
- **AND** if no range is set, the system imports all available entries

#### Scenario: Import by entry range
- **WHEN** the user sets an entry range such as "1-5" or "100-200"
- **THEN** the system imports only entries within that range

#### Scenario: Calendar stamp toggle
- **WHEN** the user enables calendar stamp mode
- **THEN** the system includes a calendar stamp in each created note

### Requirement: Dry Run and Summary Output
The system SHALL provide a dry run summary and a post-import summary that reflect the chosen settings.

#### Scenario: Dry run summary
- **WHEN** the user runs an import in dry run mode
- **THEN** the system reports how many entries would be imported
- **AND** does not create any notes or calendar entries

#### Scenario: Post-import summary
- **WHEN** the import finishes
- **THEN** the system reports counts for imported, skipped, and failed entries
- **AND** notes if entry range limited the run
- **AND** reports whether calendar stamp mode was enabled
