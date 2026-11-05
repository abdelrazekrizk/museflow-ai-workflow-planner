"""InputHandler: Normalize and validate user input for MuseFlow.

Responsibility: Accept, validate, and normalize user input (project brief + optional context)
before passing to prompt construction.

Acceptance Criteria (Requirement 1):
- Accept text input of 50–2000 characters
- Handle bullet points, prose, and mixed formats
- Gracefully handle missing information
- Preserve structure (bullets, line breaks)
- Validate optional context fields (≤1000 chars each)
"""

from typing import Dict, Optional, Tuple


class InputHandler:
    """Handles input normalization and validation."""

    # Constraints from Requirement 1
    MIN_BRIEF_LENGTH = 50
    MAX_BRIEF_LENGTH = 2000
    MAX_CONTEXT_FIELD_LENGTH = 1000

    # Valid context field names
    VALID_CONTEXT_FIELDS = {
        "team_size",
        "budget",
        "constraints",
        "architecture_notes",
    }

    @staticmethod
    def normalize(
        brief: str, context: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Normalize and validate user input.

        Args:
            brief: User-provided project brief (50–2000 chars)
            context: Optional context dict with keys: team_size, budget, constraints, architecture_notes

        Returns:
            Tuple of (normalized_brief, processed_context)

        Raises:
            ValueError: If input violates constraints

        Reference: Requirement 1 (Accept and Normalize User Input)
        """
        # Validate brief length
        brief_stripped = brief.strip()

        if len(brief_stripped) < InputHandler.MIN_BRIEF_LENGTH:
            raise ValueError(
                f"Brief must be at least {InputHandler.MIN_BRIEF_LENGTH} characters. "
                f"Got {len(brief_stripped)} characters."
            )

        if len(brief_stripped) > InputHandler.MAX_BRIEF_LENGTH:
            raise ValueError(
                f"Brief exceeds maximum {InputHandler.MAX_BRIEF_LENGTH} characters. "
                f"Got {len(brief_stripped)} characters."
            )

        # Normalize brief: preserve structure, standardize line endings
        normalized_brief = InputHandler._normalize_text(brief_stripped)

        # Process context
        processed_context = InputHandler._process_context(context)

        return normalized_brief, processed_context

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text: trim, standardize line endings, preserve bullets."""
        # Replace Windows/Mac line endings with Unix
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Trim leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def _process_context(context: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Process and validate optional context.

        Args:
            context: Optional context dict

        Returns:
            Processed context dict (trimmed, validated)

        Raises:
            ValueError: If context field exceeds max length or has invalid key

        Reference: Requirement 2 (Optional Context Injection)
        """
        if not context:
            return {}

        processed = {}

        for key, value in context.items():
            # Validate key
            if key not in InputHandler.VALID_CONTEXT_FIELDS:
                raise ValueError(
                    f"Invalid context field '{key}'. "
                    f"Valid fields: {', '.join(InputHandler.VALID_CONTEXT_FIELDS)}"
                )

            # Validate and trim value
            if not value:
                continue  # Skip empty fields

            value_str = str(value).strip()

            if len(value_str) > InputHandler.MAX_CONTEXT_FIELD_LENGTH:
                # Trim and warn
                print(
                    f"⚠ Context field '{key}' exceeds {InputHandler.MAX_CONTEXT_FIELD_LENGTH} chars. "
                    f"Trimming from {len(value_str)} to {InputHandler.MAX_CONTEXT_FIELD_LENGTH}."
                )
                value_str = value_str[: InputHandler.MAX_CONTEXT_FIELD_LENGTH]

            processed[key] = value_str

        return processed

    @staticmethod
    def validate_input_only(
        brief: str, context: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate input without raising exceptions. Returns validation result.

        Args:
            brief: User-provided project brief
            context: Optional context dict

        Returns:
            Tuple of (is_valid, error_message_or_None)
        """
        try:
            brief_stripped = brief.strip()

            if len(brief_stripped) < InputHandler.MIN_BRIEF_LENGTH:
                return (
                    False,
                    f"Brief must be at least {InputHandler.MIN_BRIEF_LENGTH} characters.",
                )

            if len(brief_stripped) > InputHandler.MAX_BRIEF_LENGTH:
                return (False, f"Brief exceeds maximum {InputHandler.MAX_BRIEF_LENGTH} characters.")

            if context:
                for key in context.keys():
                    if key not in InputHandler.VALID_CONTEXT_FIELDS:
                        return (False, f"Invalid context field: '{key}'")

                    value_len = len(str(context[key]))
                    if value_len > InputHandler.MAX_CONTEXT_FIELD_LENGTH:
                        return (
                            False,
                            f"Context field '{key}' exceeds {InputHandler.MAX_CONTEXT_FIELD_LENGTH} chars.",
                        )

            return (True, None)

        except Exception as e:
            return (False, str(e))
