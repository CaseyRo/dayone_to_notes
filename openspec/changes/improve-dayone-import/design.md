# Design: Improve Day One Importer

## Context
The current Day One importer has several issues:
1. Newlines in note text are escaped for AppleScript but not properly rendered as line breaks in Apple Notes
2. Day One JSON exports contain markdown formatting that should be preserved (Notes supports markdown natively)
3. Tags are not being applied correctly using the current AppleScript approach
4. No validation that Notes app is running before import attempts

## Goals / Non-Goals

### Goals
- Fix newline handling so line breaks are preserved in imported notes
- Preserve markdown formatting from Day One exports (Notes supports markdown)
- Fix tag application to work correctly in Apple Notes
- Add pre-flight check to ensure Notes app is running before import

### Non-Goals
- Converting markdown to rich text (Notes handles markdown natively)
- Complex markdown processing or validation
- Tag conversion or normalization (use Day One tags as-is)

## Decisions

### Decision: Handle newlines using AppleScript return character
**Rationale**: 
- Current implementation escapes `\n` to `\\n` for AppleScript string literals, but this doesn't create actual line breaks in the note body
- AppleScript interprets `return` as a newline character
- We can replace `\n` with AppleScript's `return` in the script, or use proper string construction

**Alternatives considered**:
- Using `ASCII character 10`: Less readable
- Setting body line by line: More complex, slower
- Using `return` directly in AppleScript string: Most straightforward

### Decision: Preserve markdown as-is
**Rationale**:
- Apple Notes supports markdown natively since macOS 11+
- Day One exports already contain markdown syntax
- No conversion needed - just ensure markdown text is preserved in the note body

**Alternatives considered**:
- Converting markdown to rich text: Unnecessary, Notes handles markdown
- Stripping markdown: Would lose formatting information

### Decision: Use proper AppleScript tag syntax
**Rationale**:
- Current implementation tries `tags of newNote` which may not work correctly
- Need to research correct AppleScript API for setting tags in Notes
- May need to use `name` property of tags or different approach

**Alternatives considered**:
- Adding hashtags to body text: Not ideal, these aren't functional tags
- Using tag property correctly: Need to verify correct syntax

### Decision: Check Notes app status before import
**Rationale**:
- Import will fail if Notes isn't running
- Better UX to check upfront and provide clear error message
- Can use AppleScript `application "Notes" is running` check

**Alternatives considered**:
- Try-catch approach: Less user-friendly, fails after starting
- Auto-launch Notes: May require additional permissions
- Pre-flight check: Best UX, fails fast with clear message

## Risks / Trade-offs

### Risk: Newline handling may vary by macOS version
**Mitigation**: Test on target macOS versions, use standard AppleScript `return` character

### Risk: Tag API may not be available on all macOS versions
**Mitigation**: Fallback to body hashtags with clear documentation of limitations

### Risk: Markdown preservation depends on Notes version
**Mitigation**: Verify Notes markdown support, ensure we're not modifying the text unnecessarily

## Open Questions

- What is the correct AppleScript syntax for setting tags in Apple Notes?
- Does the tag property work on all supported macOS versions?
- Should we attempt to auto-launch Notes if not running, or just error out?
