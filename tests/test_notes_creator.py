"""Tests for NotesCreator class."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dayone_import import NotesCreator


class TestNotesCreator:
    """Tests for Apple Notes creation (mocked AppleScript)."""

    @pytest.fixture
    def creator(self):
        """Create a NotesCreator instance in dry-run mode."""
        return NotesCreator(folder_name="Test Folder", dry_run=True)

    @pytest.fixture
    def creator_real(self):
        """Create a NotesCreator without dry-run (for testing AppleScript generation)."""
        return NotesCreator(folder_name="Test Folder", dry_run=False)

    def test_escape_applescript_string(self, creator):
        """Test escaping special characters for AppleScript."""
        # Test backslash escaping
        assert creator._escape_applescript_string("path\\to\\file") == "path\\\\to\\\\file"

        # Test quote escaping
        assert creator._escape_applescript_string('say "hello"') == 'say \\"hello\\"'

        # Test combined
        assert creator._escape_applescript_string('path\\to\\"file"') == 'path\\\\to\\\\\\"file\\"'

    def test_format_text_for_applescript_converts_markdown(self, creator):
        """Test that markdown is converted to HTML for AppleScript."""
        result = creator._format_text_for_applescript_body("# Header")

        # Should be wrapped in quotes
        assert result.startswith('"')
        assert result.endswith('"')

        # Should contain HTML header tag
        assert "<h1>" in result

    def test_format_text_escapes_quotes(self, creator):
        """Test that quotes in text are escaped."""
        result = creator._format_text_for_applescript_body('He said "hello"')

        # Quotes should be escaped
        assert '\\"' in result

    def test_extract_title_first_line(self, creator):
        """Test title extraction from first line."""
        text = "My Title\n\nSome content here."
        title = creator._extract_title(text)
        assert title == "My Title"

    def test_extract_title_truncates_long(self, creator):
        """Test that long titles are truncated."""
        text = "A" * 100 + "\nContent"
        title = creator._extract_title(text)
        assert len(title) <= 50
        assert title.endswith("...")

    def test_extract_title_empty_text(self, creator):
        """Test title extraction from empty text."""
        title = creator._extract_title("")
        assert title == "Untitled Note"

    def test_extract_title_whitespace_only(self, creator):
        """Test title extraction from whitespace-only text."""
        title = creator._extract_title("   \n\n   ")
        assert title == "Untitled Note"

    def test_unique_title_first_occurrence(self, creator):
        """Test that first title is not modified."""
        title = creator._get_unique_title("My Note")
        assert title == "My Note"

    def test_unique_title_duplicates(self, creator):
        """Test that duplicates get numbered."""
        creator._get_unique_title("My Note")  # First
        title2 = creator._get_unique_title("My Note")  # Second
        title3 = creator._get_unique_title("My Note")  # Third

        assert title2 == "My Note 2"
        assert title3 == "My Note 3"

    def test_create_note_dry_run(self, creator, sample_entry_markdown):
        """Test note creation in dry-run mode."""
        success, output = creator.create_note(
            text=sample_entry_markdown['text'],
            photos=[],
            videos=[],
            tags=sample_entry_markdown['tags'],
            creation_date=sample_entry_markdown['creationDate'],
            entry_uuid=sample_entry_markdown['uuid']
        )

        assert success is True
        assert output == "dry-run"

    def test_create_note_tracks_created(self, creator):
        """Test that created notes are tracked."""
        creator.create_note(
            text="Test Note",
            photos=[],
            videos=[],
            tags=[],
            entry_uuid="TEST1"
        )

        assert "Test Note" in creator.created_notes

    def test_create_note_prepends_formatted_date(self, creator_real):
        """Test that creation date is prepended to note body."""
        captured = {}

        def fake_execute(script):
            captured["script"] = script
            return True, "ok"

        creator_real._execute_applescript = fake_execute

        creator_real.create_note(
            text="Date test note",
            photos=[],
            videos=[],
            tags=[],
            creation_date="2024-01-15T10:30:00",
            entry_uuid="DATE1"
        )

        script = captured.get("script", "")
        # Date should be prepended with emoji, not set via AppleScript
        assert "set creation date of newNote" not in script
        assert "📅" in script
        assert "January 15, 2024" in script
        assert "Date test note" in script

    def test_create_note_fallback_on_unparseable_date(self, creator_real):
        """Test that unparseable dates are still prepended with raw date."""
        captured = {}

        def fake_execute(script):
            captured["script"] = script
            return True, "ok"

        creator_real._execute_applescript = fake_execute

        creator_real.create_note(
            text="Bad date note",
            photos=[],
            videos=[],
            tags=[],
            creation_date="not-a-date",
            entry_uuid="DATE2"
        )

        script = captured.get("script", "")
        assert "set creation date of newNote" not in script
        # Raw date should still be prepended with emoji
        assert "📅 not-a-date" in script
        assert "Bad date note" in script

    @patch('subprocess.run')
    def test_execute_applescript_success(self, mock_run, creator_real):
        """Test successful AppleScript execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="success",
            stderr=""
        )

        success, output = creator_real._execute_applescript("tell app to do thing")

        assert success is True
        assert output == "success"
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_execute_applescript_failure(self, mock_run, creator_real):
        """Test failed AppleScript execution."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error message"
        )

        success, output = creator_real._execute_applescript("tell app to do thing")

        assert success is False
        assert "error message" in output

    @patch('subprocess.run')
    def test_execute_applescript_timeout(self, mock_run, creator_real):
        """Test AppleScript execution timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=30)

        success, output = creator_real._execute_applescript("tell app to do thing")

        assert success is False
        assert "timed out" in output.lower()

    def test_ensure_folder_exists_no_folder(self, creator):
        """Test ensure_folder_exists with no folder name."""
        creator_no_folder = NotesCreator(folder_name=None, dry_run=True)
        result = creator_no_folder.ensure_folder_exists()
        assert result is True

    def test_markdown_converter_initialized(self, creator):
        """Test that markdown converter is initialized."""
        assert hasattr(creator, 'markdown_converter')
        assert creator.markdown_converter is not None


class TestNotesCreatorIntegration:
    """Integration tests for NotesCreator (still mocked but testing more flow)."""

    @pytest.fixture
    def creator(self):
        """Create a NotesCreator in dry-run mode."""
        return NotesCreator(folder_name="Day One Import", dry_run=True)

    def test_create_multiple_notes(self, creator, sample_entry_markdown, sample_entry_plain):
        """Test creating multiple notes."""
        # Create first note
        success1, _ = creator.create_note(
            text=sample_entry_markdown['text'],
            photos=[],
            videos=[],
            tags=sample_entry_markdown['tags'],
            entry_uuid=sample_entry_markdown['uuid']
        )

        # Create second note
        success2, _ = creator.create_note(
            text=sample_entry_plain['text'],
            photos=[],
            videos=[],
            tags=[],
            entry_uuid=sample_entry_plain['uuid']
        )

        assert success1 is True
        assert success2 is True
        assert len(creator.created_notes) == 2

    def test_create_note_with_tags_adds_hashtags(self, creator):
        """Test that tags are converted to hashtags."""
        # In dry-run mode we can't verify the actual AppleScript,
        # but we can verify the method completes without error
        success, _ = creator.create_note(
            text="Note with tags",
            photos=[],
            videos=[],
            tags=["tag1", "tag2", "multi-word-tag"],
            entry_uuid="TAG_TEST"
        )

        assert success is True
