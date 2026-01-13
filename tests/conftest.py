"""Pytest fixtures for Day One import tests."""

import json
import pytest
from pathlib import Path
import tempfile
import shutil


# Sample Day One entry with various markdown formatting
SAMPLE_ENTRY_MARKDOWN = {
    "uuid": "ABC123DEF456",
    "text": """# My Journal Entry

This is a paragraph with **bold text** and *italic text*.

## Subheading

Here's a list:
- Item one
- Item two
- Item three

And a numbered list:
1. First thing
2. Second thing
3. Third thing

Some more text with a [link](https://example.com).
""",
    "creationDate": "2024-01-15T10:30:00Z",
    "photos": [],
    "videos": [],
    "tags": ["journal", "test"]
}

# Simple entry without markdown
SAMPLE_ENTRY_PLAIN = {
    "uuid": "PLAIN123",
    "text": "Just a simple note without any formatting.",
    "creationDate": "2024-02-20T14:00:00Z",
    "photos": [],
    "videos": [],
    "tags": []
}

# Entry with photos
SAMPLE_ENTRY_WITH_PHOTO = {
    "uuid": "PHOTO123",
    "text": "Entry with an embedded photo.\n\n![](dayone-moment://ABC123)\n\nMore text after the photo.",
    "creationDate": "2024-03-01T09:00:00Z",
    "photos": [
        {
            "identifier": "ABC123",
            "md5": "d41d8cd98f00b204e9800998ecf8427e",
            "type": "jpeg"
        }
    ],
    "videos": [],
    "tags": ["photo", "memory"]
}

# Entry with complex markdown
SAMPLE_ENTRY_COMPLEX = {
    "uuid": "COMPLEX456",
    "text": """# Weekly Review

## What went well
- **Completed project milestone** - finally done!
- *Started new habit* of morning journaling

## What could improve
1. Sleep schedule needs work
2. More exercise needed

### Notes
> This is a blockquote that might not render but should be preserved.

Some `inline code` and special characters: "quotes" & <angles>.
""",
    "creationDate": "2024-03-15T18:30:00Z",
    "photos": [],
    "videos": [],
    "tags": ["weekly-review", "reflection"]
}


@pytest.fixture
def sample_entry_markdown():
    """Return a sample Day One entry with markdown formatting."""
    return SAMPLE_ENTRY_MARKDOWN.copy()


@pytest.fixture
def sample_entry_plain():
    """Return a sample Day One entry without formatting."""
    return SAMPLE_ENTRY_PLAIN.copy()


@pytest.fixture
def sample_entry_with_photo():
    """Return a sample Day One entry with a photo reference."""
    return SAMPLE_ENTRY_WITH_PHOTO.copy()


@pytest.fixture
def sample_entry_complex():
    """Return a sample Day One entry with complex markdown."""
    return SAMPLE_ENTRY_COMPLEX.copy()


@pytest.fixture
def sample_dayone_json(sample_entry_markdown, sample_entry_plain):
    """Return a complete Day One JSON structure with multiple entries."""
    return {
        "entries": [sample_entry_markdown, sample_entry_plain]
    }


@pytest.fixture
def temp_export_dir(sample_dayone_json):
    """Create a temporary Day One export directory structure."""
    temp_dir = tempfile.mkdtemp()
    export_path = Path(temp_dir)

    # Create JSON file
    json_path = export_path / "Journal.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_dayone_json, f)

    # Create photos and videos directories
    (export_path / "photos").mkdir()
    (export_path / "videos").mkdir()

    yield export_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_export_dir_multiple_json():
    """Create a temporary export directory with multiple JSON files."""
    temp_dir = tempfile.mkdtemp()
    export_path = Path(temp_dir)

    # Create first JSON file
    json1 = {
        "entries": [SAMPLE_ENTRY_MARKDOWN.copy()]
    }
    with open(export_path / "Journal.json", 'w', encoding='utf-8') as f:
        json.dump(json1, f)

    # Create second JSON file
    json2 = {
        "entries": [SAMPLE_ENTRY_PLAIN.copy(), SAMPLE_ENTRY_COMPLEX.copy()]
    }
    with open(export_path / "Work.json", 'w', encoding='utf-8') as f:
        json.dump(json2, f)

    # Create photos and videos directories
    (export_path / "photos").mkdir()
    (export_path / "videos").mkdir()

    yield export_path

    # Cleanup
    shutil.rmtree(temp_dir)
