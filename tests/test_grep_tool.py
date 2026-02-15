"""
Tests for the grep functionality.
"""
import uuid

from geai.tools.grep_tool import grep_impl, GrepResult, GrepLine


class TestGrepImpl:
    """Test suite for grep_impl function."""

    def test_grep_simple_text(self):
        """Test basic grep search for simple text."""
        result = grep_impl("hello")
        
        assert isinstance(result, GrepResult)
        assert result.success is True
        assert len(result.lines) > 0
        assert all(isinstance(line, GrepLine) for line in result.lines)

    def test_grep_with_regex(self):
        """Test grep with regex pattern."""
        result = grep_impl(r"\d+", is_regex=True)
        
        assert isinstance(result, GrepResult)
        assert result.success is True
        assert len(result.lines) > 0
        # Should find lines with numbers
        assert any(any(char.isdigit() for char in line.matched_line) for line in result.lines)

    def test_grep_no_matches(self):
        """Test grep when no matches are found."""
        result = grep_impl(str(uuid.uuid4()))
        
        assert isinstance(result, GrepResult)
        assert result.success is True
        assert len(result.lines) == 0

    def test_grep_empty_search_text(self):
        """Test grep with empty search text."""
        result = grep_impl("")
        
        assert isinstance(result, GrepResult)
        # Empty search should either match everything or return empty result
        # depending on implementation
        assert result.success is True

    def test_grep_line_model(self):
        """Test the GrepLine model structure."""
        line = GrepLine(
            file_name="test.txt",
            line=1,
            matched_line="hello world"
        )
        
        assert line.file_name == "test.txt"
        assert line.line == 1
        assert line.matched_line == "hello world"

    def test_grep_result_model(self):
        """Test the GrepResult model structure."""
        result = GrepResult(
            lines=[],
            success=True,
            error_message=None
        )
        
        assert result.lines == []
        assert result.success is True
        assert result.error_message is None

    def test_grep_result_with_error(self):
        """Test GrepResult with error message."""
        result = GrepResult(
            lines=[],
            success=False,
            error_message="Test error message"
        )
        
        assert result.lines == []
        assert result.success is False
        assert result.error_message == "Test error message"

    def test_grep_result_with_lines_and_error(self):
        """Test GrepResult with both lines and error message."""
        line = GrepLine(
            file_name="test.txt",
            line=1,
            matched_line="test line"
        )
        
        result = GrepResult(
            lines=[line],
            success=True,
            error_message=None
        )
        
        assert len(result.lines) == 1
        assert result.lines[0].file_name == "test.txt"
        assert result.lines[0].line == 1
        assert result.lines[0].matched_line == "test line"
        assert result.success is True
        assert result.error_message is None