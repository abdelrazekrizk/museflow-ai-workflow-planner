"""Tests for PromptConstructor component."""

from src.museflow.prompt_constructor import PromptConstructor


class TestPromptConstructorBuildPrompt:
    """Test prompt construction with various inputs."""

    def test_build_prompt_basic_brief_only(self):
        """Build prompt with brief only (no context)."""
        brief = "Build a Python async web scraper for e-commerce sites"
        prompt = PromptConstructor.build_prompt(brief, {})

        assert "MuseFlow" in prompt
        assert brief in prompt
        assert "OUTPUT SCHEMA" in prompt
        assert "EXAMPLE OUTPUT" in prompt
        assert prompt.endswith("Output ONLY valid JSON, no additional text.")

    def test_build_prompt_with_context(self):
        """Build prompt with context fields."""
        brief = "Migrate from monolith to microservices" * 4  # Make it long enough
        context = {
            "team_size": "5",
            "budget": "limited",
            "constraints": "6-month deadline"
        }
        prompt = PromptConstructor.build_prompt(brief, context)

        assert "OPTIONAL CONTEXT:" in prompt
        assert "Team Size: 5" in prompt
        assert "Budget: limited" in prompt
        assert "Constraints: 6-month deadline" in prompt

    def test_build_prompt_retry_generic_task(self):
        """Build retry prompt for generic task failure."""
        brief = "x" * 100
        prompt = PromptConstructor.build_prompt(
            brief,
            {},
            retry_count=1,
            failure_type="generic_task"
        )

        assert "ERROR FEEDBACK FROM LAST ATTEMPT" in prompt
        assert "generic" in prompt.lower() or "specific" in prompt.lower()

    def test_build_prompt_retry_metric_invalid(self):
        """Build retry prompt for invalid metric failure."""
        brief = "y" * 100
        prompt = PromptConstructor.build_prompt(
            brief,
            {},
            retry_count=1,
            failure_type="metric_invalid"
        )

        assert "ERROR FEEDBACK FROM LAST ATTEMPT" in prompt
        assert "metric" in prompt.lower() or "quantified" in prompt.lower()

    def test_build_prompt_retry_vague_mitigation(self):
        """Build retry prompt for vague mitigation failure."""
        brief = "z" * 100
        prompt = PromptConstructor.build_prompt(
            brief,
            {},
            retry_count=1,
            failure_type="vague_mitigation"
        )

        assert "ERROR FEEDBACK FROM LAST ATTEMPT" in prompt
        assert "concrete" in prompt.lower() or "mitigation" in prompt.lower()

    def test_build_prompt_includes_schema(self):
        """Prompt always includes schema specification."""
        brief = "a" * 100
        prompt = PromptConstructor.build_prompt(brief, {})

        # Check for schema JSON structure
        assert '"summary"' in prompt
        assert '"objectives"' in prompt
        assert '"tasks"' in prompt
        assert '"risks"' in prompt
        assert '"assumptions"' in prompt
        assert '"nextActions"' in prompt

    def test_build_prompt_includes_demo_example(self):
        """Prompt includes demo example output."""
        brief = "b" * 100
        prompt = PromptConstructor.build_prompt(brief, {})

        # Check for key elements of demo example
        assert "microservice" in prompt.lower() or "10x" in prompt
        assert "EXAMPLE OUTPUT" in prompt


class TestPromptConstructorStaticMethods:
    """Test static method accessors."""

    def test_get_schema_specification(self):
        """get_schema_specification returns valid JSON structure."""
        schema = PromptConstructor.get_schema_specification()

        assert schema is not None
        assert '"summary"' in schema
        assert '"tasks"' in schema

    def test_get_system_role(self):
        """get_system_role returns system instructions."""
        role = PromptConstructor.get_system_role()

        assert "MuseFlow" in role
        assert "planning" in role.lower()

    def test_get_demo_example(self):
        """get_demo_example returns valid JSON demo."""
        demo = PromptConstructor.get_demo_example()

        assert demo is not None
        assert '"summary"' in demo
        assert '"objectives"' in demo
