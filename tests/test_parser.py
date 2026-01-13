"""Tests for DayOneParser class."""

import json
import pytest
from pathlib import Path
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dayone_import import DayOneParser


class TestDayOneParser:
    """Tests for parsing Day One JSON exports."""

    def test_parse_valid_json(self, temp_export_dir):
        """Test parsing a valid Day One JSON file."""
        json_path = temp_export_dir / "Journal.json"
        parser = DayOneParser(json_path)
        entries = parser.parse()

        assert len(entries) == 2
        assert entries[0]['uuid'] == 'ABC123DEF456'
        assert entries[1]['uuid'] == 'PLAIN123'

    def test_parse_entry_data(self, sample_entry_markdown):
        """Test extracting data from an entry."""
        data = DayOneParser.get_entry_data(sample_entry_markdown)

        assert data['uuid'] == 'ABC123DEF456'
        assert '# My Journal Entry' in data['text']
        assert data['creationDate'] == '2024-01-15T10:30:00Z'
        assert data['tags'] == ['journal', 'test']
        assert data['photos'] == []
        assert data['videos'] == []

    def test_parse_entry_with_photos(self, sample_entry_with_photo):
        """Test extracting data from an entry with photos."""
        data = DayOneParser.get_entry_data(sample_entry_with_photo)

        assert len(data['photos']) == 1
        assert data['photos'][0]['identifier'] == 'ABC123'
        assert data['photos'][0]['md5'] == 'd41d8cd98f00b204e9800998ecf8427e'

    def test_parse_missing_file(self):
        """Test parsing a non-existent file raises error."""
        parser = DayOneParser(Path("/nonexistent/file.json"))

        with pytest.raises(FileNotFoundError):
            parser.parse()

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            temp_path = Path(f.name)

        try:
            parser = DayOneParser(temp_path)
            with pytest.raises(json.JSONDecodeError):
                parser.parse()
        finally:
            temp_path.unlink()

    def test_parse_json_without_entries(self):
        """Test parsing JSON without entries array raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not_entries": []}, f)
            temp_path = Path(f.name)

        try:
            parser = DayOneParser(temp_path)
            with pytest.raises(ValueError, match="does not contain 'entries'"):
                parser.parse()
        finally:
            temp_path.unlink()

    def test_parse_empty_entries(self):
        """Test parsing JSON with empty entries array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"entries": []}, f)
            temp_path = Path(f.name)

        try:
            parser = DayOneParser(temp_path)
            entries = parser.parse()
            assert entries == []
        finally:
            temp_path.unlink()

    def test_get_entry_data_missing_fields(self):
        """Test extracting data from entry with missing fields."""
        minimal_entry = {"uuid": "MIN123"}
        data = DayOneParser.get_entry_data(minimal_entry)

        assert data['uuid'] == 'MIN123'
        assert data['text'] == ''
        assert data['creationDate'] == ''
        assert data['photos'] == []
        assert data['videos'] == []
        assert data['tags'] == []
