## 1. Project Setup
- [x] 1.1 Create Python project structure (main script, requirements.txt)
- [x] 1.2 Set up virtual environment and dependencies
- [x] 1.3 Create README with usage instructions

## 2. Day One JSON Parser
- [x] 2.1 Implement JSON file reader that loads Day One export
- [x] 2.2 Extract entries array and parse entry structure
- [x] 2.3 Parse text, photos, videos, dates, and metadata from entries
- [x] 2.4 Add validation for required fields and error handling for malformed JSON
- [ ] 2.5 Write unit tests for JSON parsing

## 3. Media File Resolution
- [x] 3.1 Implement function to scan photos/ directory and build file index
- [x] 3.2 Implement function to scan videos/ directory and build file index
- [x] 3.3 Create media file resolver that matches identifiers to files
- [x] 3.4 Add MD5 hash matching as fallback for identifier matching
- [x] 3.5 Handle missing media files gracefully with warnings
- [ ] 3.6 Write unit tests for media resolution

## 4. AppleScript Integration
- [x] 4.1 Research and document AppleScript commands for Notes app
- [x] 4.2 Create AppleScript template for creating notes with text
- [x] 4.3 Extend AppleScript to attach images to notes
- [x] 4.4 Extend AppleScript to attach videos to notes
- [x] 4.5 Implement folder creation in AppleScript (create if doesn't exist)
- [x] 4.6 Implement tag application in AppleScript
- [x] 4.7 Test AppleScript execution via osascript command
- [x] 4.8 Add error handling for AppleScript failures

## 5. Python-AppleScript Bridge
- [x] 5.1 Implement function to execute AppleScript from Python using subprocess
- [x] 5.2 Create wrapper functions for note creation with parameters
- [x] 5.3 Implement media attachment function that passes file paths to AppleScript
- [x] 5.4 Add parameter escaping and sanitization for AppleScript
- [ ] 5.5 Write integration tests for note creation

## 6. Main Import Logic
- [x] 6.1 Create main import function that orchestrates parsing, resolution, and creation
- [x] 6.2 Implement batch processing loop for multiple entries
- [x] 6.3 Add progress reporting (console output)
- [x] 6.4 Implement date preservation (attempt to set creation date)
- [x] 6.5 Add folder creation/organization logic (create folder if needed)
- [x] 6.6 Implement duplicate detection and numbering (e.g., "Title 2", "Title 3")
- [x] 6.7 Add tag application logic (preserve Day One tags as Apple Notes tags)
- [x] 6.8 Collect errors and generate summary report

## 7. Command-Line Interface
- [x] 7.1 Create CLI argument parser (export directory, target folder, options)
- [x] 7.2 Add --dry-run option for testing without creating notes
- [x] 7.3 Add --verbose option for detailed logging
- [x] 7.4 Add --folder option to specify target Notes folder
- [x] 7.5 Implement help text and usage examples

## 8. Error Handling and Logging
- [x] 8.1 Set up logging framework with appropriate levels
- [x] 8.2 Add error handling for all major operations
- [x] 8.3 Create error summary report generator
- [x] 8.4 Add validation for export directory structure
- [ ] 8.5 Test error scenarios (missing files, Notes app closed, etc.)

## 9. Testing and Validation
- [ ] 9.1 Test with sample Day One export (small dataset)
- [ ] 9.2 Test with entry containing only text
- [ ] 9.3 Test with entry containing text and images
- [ ] 9.4 Test with entry containing text and videos
- [ ] 9.5 Test with entry containing text, images, and videos
- [ ] 9.6 Test folder creation (auto-create if doesn't exist)
- [ ] 9.7 Test duplicate handling (creates numbered copies)
- [ ] 9.8 Test tag preservation (Day One tags applied to Notes)
- [ ] 9.9 Test error handling with missing media files
- [ ] 9.10 Test batch processing with large export
- [ ] 9.11 Verify date preservation works correctly

## 10. Documentation
- [x] 10.1 Update README with installation instructions
- [x] 10.2 Add usage examples and command-line options
- [x] 10.3 Document folder organization behavior (auto-creation)
- [x] 10.4 Document duplicate handling behavior (numbered copies)
- [x] 10.5 Document tag preservation from Day One
- [x] 10.6 Add troubleshooting section for common issues
- [x] 10.7 Document limitations and known issues
