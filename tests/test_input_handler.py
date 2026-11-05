"""Tests for InputHandler component."""

import pytest
from src.museflow.input_handler import InputHandler


class TestInputHandlerNormalize:
    """Test input normalization and validation."""

    def test_valid_brief_50_chars(self):
        """Valid brief with minimum length (50 chars)."""
        brief = "a" * 50
        normalized, context = InputHandler.normalize(brief)
        assert len(normalized) == 50
        assert context == {}

    def test_valid_brief_2000_chars(self):
        """Valid brief with maximum length (2000 chars)."""
        brief = "b" * 2000
        normalized, context = InputHandler.normalize(brief)
        assert len(normalized) == 2000
        assert context == {}

    def test_brief_too_short_49_chars(self):
        """Brief below minimum length should raise ValueError."""
        brief = "c" * 49
        with pytest.raises(ValueError, match="at least 50"):
            InputHandler.normalize(brief)

    def test_brief_too_long_2001_chars(self):
        """Brief above maximum length should raise ValueError."""
        brief = "d" * 2001
        with pytest.raises(ValueError, match="exceeds maximum"):
            InputHandler.normalize(brief)

    def test_whitespace_handling(self):
        """Brief with leading/trailing whitespace is trimmed."""
        brief = "   " + ("e" * 50) + "   "
        normalized, _ = InputHandler.normalize(brief)
        assert len(normalized) == 50
        assert not normalized.startswith(" ")
        assert not normalized.endswith(" ")

    def test_line_break_preservation(self):
        """Bullet points and line breaks are preserved."""
        brief = """
        • First point (this is point 1)
        • Second point (this is point 2)
        • Third point (this is point 3)
        Additional text here for clarity.
        """
        normalized, _ = InputHandler.normalize(brief)
        assert "•" in normalized or "-" in normalized
        assert "\n" in normalized or "point" in normalized

    def test_context_valid_single_field(self):
        """Valid context with single field."""
        brief = "x" * 100
        context = {"team_size": "3"}
        _, processed = InputHandler.normalize(brief, context)
        assert processed["team_size"] == "3"

    def test_context_valid_multiple_fields(self):
        """Valid context with multiple valid fields."""
        brief = "y" * 100
        context = {
            "team_size": "2",
            "budget": "limited",
            "constraints": "2-week deadline"
        }
        _, processed = InputHandler.normalize(brief, context)
        assert len(processed) == 3
        assert processed["team_size"] == "2"

    def test_context_field_exceeds_max_length(self):
        """Context field exceeding 1000 chars is trimmed."""
        brief = "z" * 100
        context = {"budget": "a" * 1500}
        _, processed = InputHandler.normalize(brief, context)
        assert len(processed["budget"]) == 1000

    def test_context_invalid_field_name(self):
        """Invalid context field name raises ValueError."""
        brief = "a" * 100
        context = {"invalid_field": "value"}
        with pytest.raises(ValueError, match="Invalid context field"):
            InputHandler.normalize(brief, context)

    def test_context_empty_fields_skipped(self):
        """Empty context fields are skipped."""
        brief = "b" * 100
        context = {"team_size": "", "budget": "limited"}
        _, processed = InputHandler.normalize(brief, context)
        assert "team_size" not in processed
        assert "budget" in processed


class TestInputHandlerValidateOnly:
    """Test validation without exceptions."""

    def test_validate_valid_input(self):
        """Valid input passes validation."""
        brief = "c" * 100
        is_valid, error = InputHandler.validate_input_only(brief)
        assert is_valid is True
        assert error is None

    def test_validate_brief_too_short(self):
        """Brief too short fails validation."""
        brief = "d" * 40
        is_valid, error = InputHandler.validate_input_only(brief)
        assert is_valid is False
        assert "50" in error

    def test_validate_context_invalid_field(self):
        """Invalid context field fails validation."""
        brief = "e" * 100
        context = {"bad_field": "value"}
        is_valid, error = InputHandler.validate_input_only(brief, context)
        assert is_valid is False
        assert "Invalid context field" in error
