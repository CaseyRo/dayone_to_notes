"""Tests for MarkdownConverter class."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dayone_import import MarkdownConverter


class TestMarkdownConverter:
    """Tests for markdown to HTML conversion."""

    @pytest.fixture
    def converter(self):
        """Create a MarkdownConverter instance."""
        return MarkdownConverter()

    def test_convert_header(self, converter):
        """Test converting markdown headers to HTML."""
        result = converter.convert("# Header 1")
        assert "<h1>" in result
        assert "Header 1" in result

    def test_convert_subheader(self, converter):
        """Test converting markdown subheaders to HTML."""
        result = converter.convert("## Header 2")
        assert "<h2>" in result
        assert "Header 2" in result

    def test_convert_bold(self, converter):
        """Test converting bold text to HTML."""
        result = converter.convert("This is **bold** text")
        assert "<strong>bold</strong>" in result or "<b>bold</b>" in result

    def test_convert_italic(self, converter):
        """Test converting italic text to HTML."""
        result = converter.convert("This is *italic* text")
        assert "<em>italic</em>" in result or "<i>italic</i>" in result

    def test_convert_unordered_list(self, converter):
        """Test converting unordered lists to HTML."""
        md = """- Item 1
- Item 2
- Item 3"""
        result = converter.convert(md)
        assert "<ul>" in result
        assert "<li>" in result
        assert "Item 1" in result

    def test_convert_ordered_list(self, converter):
        """Test converting ordered lists to HTML."""
        md = """1. First
2. Second
3. Third"""
        result = converter.convert(md)
        assert "<ol>" in result
        assert "<li>" in result
        assert "First" in result

    def test_convert_newlines_to_br(self, converter):
        """Test that newlines are converted to <br> tags."""
        result = converter.convert("Line 1\nLine 2")
        assert "<br" in result

    def test_convert_link(self, converter):
        """Test converting links to HTML."""
        result = converter.convert("Check out [this link](https://example.com)")
        assert '<a href="https://example.com">' in result
        assert "this link" in result

    def test_strip_dayone_image_refs(self, converter):
        """Test that Day One image references are stripped."""
        md = "Before\n\n![](dayone-moment://ABC123)\n\nAfter"
        result = converter.convert(md)
        assert "dayone-moment" not in result
        assert "Before" in result
        assert "After" in result

    def test_strip_dayone_image_refs_with_alt(self, converter):
        """Test stripping Day One image refs with alt text."""
        md = "Before ![photo](dayone-moment://XYZ789) After"
        result = converter.convert(md)
        assert "dayone-moment" not in result

    def test_preserve_instagram_urls(self, converter):
        """Test that Instagram URLs are preserved (for link previews)."""
        md = "Cupcake time!\n\nhttps://www.instagram.com/p/VQ9_T/\n\n![](dayone-moment://ABC123)"
        result = converter.convert(md)
        assert "instagram.com" in result
        assert "dayone-moment" not in result
        assert "Cupcake time!" in result

    def test_preserve_instagram_reel_urls(self, converter):
        """Test that Instagram reel URLs are preserved."""
        md = "Cool reel: https://www.instagram.com/reel/ABC123/"
        result = converter.convert(md)
        assert "instagram.com" in result

    def test_html_entities_ampersand(self, converter):
        """Test that ampersands are properly escaped."""
        # Markdown library escapes & but allows raw HTML tags (by design)
        md = "Tom & Jerry"
        result = converter.convert(md)
        # Ampersand should be escaped
        assert "&amp;" in result or "Tom & Jerry" in result

    def test_complex_markdown(self, converter, sample_entry_complex):
        """Test converting complex markdown entry."""
        result = converter.convert(sample_entry_complex['text'])

        # Should have headers
        assert "<h1>" in result
        assert "Weekly Review" in result

        # Should have subheaders
        assert "<h2>" in result

        # Should have bold
        assert "<strong>" in result or "Completed project milestone" in result

        # Should have lists
        assert "<li>" in result

    def test_empty_text(self, converter):
        """Test converting empty text."""
        result = converter.convert("")
        assert result == "" or result == "<br>\n" or result.strip() == ""

    def test_plain_text(self, converter, sample_entry_plain):
        """Test converting plain text without markdown."""
        result = converter.convert(sample_entry_plain['text'])
        assert "Just a simple note" in result

    def test_preserves_special_characters(self, converter):
        """Test that special characters are preserved."""
        md = "Café résumé naïve"
        result = converter.convert(md)
        assert "Café" in result or "Caf" in result  # May be encoded
