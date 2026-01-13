## 1. Fix Newline Handling
- [x] 1.1 Investigate current newline escaping in `_escape_applescript_string`
- [x] 1.2 Update AppleScript note creation to properly handle newlines in body text
- [ ] 1.3 Test that multi-line entries preserve line breaks correctly

## 2. Preserve Markdown Formatting
- [x] 2.1 Verify that Day One JSON export text contains markdown syntax
- [x] 2.2 Ensure markdown formatting is preserved when setting note body (Notes supports markdown natively)
- [ ] 2.3 Test with entries containing markdown (headers, lists, bold, italic, links, etc.)
- [ ] 2.4 Verify markdown renders correctly in Apple Notes after import

## 3. Fix Tag Application
- [x] 3.1 Research correct AppleScript syntax for setting tags in Apple Notes
- [x] 3.2 Fix tag application logic in `create_note` method
- [ ] 3.3 Test tag application with single and multiple tags
- [ ] 3.4 Verify tags appear correctly in Apple Notes interface
- [x] 3.5 Handle edge cases (special characters in tags, empty tag lists)

## 4. Add Notes App Pre-flight Check
- [x] 4.1 Implement function to check if Apple Notes is running using AppleScript
- [x] 4.2 Add pre-import check before starting import process
- [x] 4.3 Provide clear error message if Notes is not running
- [ ] 4.4 Test error handling when Notes app is closed
- [ ] 4.5 Optionally: Prompt user to open Notes app if not running

## 5. Testing and Validation
- [ ] 5.1 Test import with entry containing multiple newlines
- [ ] 5.2 Test import with entry containing markdown formatting
- [ ] 5.3 Test import with entry containing tags
- [ ] 5.4 Test import when Notes app is closed (should fail gracefully)
- [ ] 5.5 Test complete import workflow with all improvements combined
