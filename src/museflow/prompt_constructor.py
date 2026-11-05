"""PromptConstructor: Build rich, context-aware prompts for Muse Spark 1.3.

Responsibility: Construct intelligent prompts that include the schema specification,
demo examples, context injection, and retry messaging.

Reference: Requirements 1, 2, 3 (Input, Context, Plan Generation)
Reference: Design Section 2.4 (Low-Level Design - Prompt Template)
"""

from typing import Optional


class PromptConstructor:
    """Builds rich prompts for Muse Spark 1.3 with context and retry logic."""

    # Static prompt components
    SYSTEM_ROLE = """You are MuseFlow, an AI workflow planning assistant. Your job is to convert a project brief or ambiguous goal into a clear, actionable execution plan.

When given a project brief, you will:
1. Understand the core challenge and constraints
2. Define clear, measurable objectives
3. Generate 4-6 specific, actionable tasks with effort estimates
4. Identify 1-3 risks with concrete mitigation strategies
5. Surface key assumptions
6. Recommend immediate next actions

All output must be valid JSON matching the schema specification below. Focus on specificity, measurability, and actionability."""

    SCHEMA_SPECIFICATION = """{
  "summary": "string (1-2 sentences, directly addresses core challenge)",
  "objectives": ["string (2-4 objectives)", "..."],
  "tasks": [
    {
      "id": "integer (1-indexed)",
      "title": "string (specific, includes metric or constraint)",
      "priority": "string (one of: high, medium, low)",
      "effort": "string (e.g., '2 days', '1 week', '8 hours')",
      "rationale": "string (why this task is important)"
    },
    "... (4-6 tasks total)"
  ],
  "risks": [
    {
      "risk": "string (problem statement)",
      "impact": "string (one of: high, medium, low)",
      "mitigation": "string (concrete strategy)"
    },
    "... (1-3 risks total)"
  ],
  "assumptions": ["string (2-4 assumptions)", "..."],
  "nextActions": ["string (2-4 immediate next actions)", "..."],
  "reasoning": "string (optional; include only if you have extended reasoning to share)"
}"""

    DEMO_EXAMPLE_OUTPUT = """{
  "summary": "Upgrade microservice for 10x load via async refactor and DB query optimization",
  "objectives": [
    "Support 10x concurrent requests without latency degradation",
    "Reduce database query time by 50% via caching",
    "Maintain backward compatibility; no breaking API changes"
  ],
  "tasks": [
    {
      "id": 1,
      "title": "Audit database queries and identify bottlenecks using slow query logs; prioritize by impact",
      "priority": "high",
      "effort": "1.5 days",
      "rationale": "Database queries are the stated primary bottleneck; this audit informs all subsequent optimization work"
    },
    {
      "id": 2,
      "title": "Refactor synchronous I/O to async/await in request handlers to reduce thread pool contention; target 10k concurrent connections",
      "priority": "high",
      "effort": "3 days",
      "rationale": "Async I/O is critical for scaling; converts thread-per-request to async pattern"
    },
    {
      "id": 3,
      "title": "Implement Redis caching with 2-hour TTL for 5 most-expensive queries; measure cache hit rate",
      "priority": "high",
      "effort": "2 days",
      "rationale": "Caching directly reduces database load and latency"
    },
    {
      "id": 4,
      "title": "Write integration tests for cached queries and async endpoints; confirm no breaking changes",
      "priority": "medium",
      "effort": "1 day",
      "rationale": "Regression testing ensures refactoring does not introduce bugs"
    }
  ],
  "risks": [
    {
      "risk": "Async refactoring introduces breaking changes in unrelated services",
      "impact": "high",
      "mitigation": "Implement changes on a feature branch; run full integration test suite before merging; use feature flags for gradual rollout"
    },
    {
      "risk": "Scope creep (e.g., requests to add new features) derails the 2-week timeline",
      "impact": "high",
      "mitigation": "Establish scope lock from day 1; document 'out of scope' for leadership; set weekly milestone reviews"
    }
  ],
  "assumptions": [
    "Database is the primary bottleneck (as stated); other bottlenecks are secondary",
    "Team has experience with Python async/await and is familiar with the codebase",
    "2-week timeline is fixed; scope is flexible within that window"
  ],
  "nextActions": [
    "Set up feature branch; document scope lock",
    "Run database slow query log analysis; identify top 5 expensive queries",
    "Design async/await refactoring strategy; identify services to refactor first",
    "Set up load test environment with baseline metrics"
  ],
  "reasoning": "The plan prioritizes database optimization (high-impact, short-duration audit first) and async I/O refactoring (addresses the root cause of connection limits). Caching provides a quick win. Testing proves the improvement. The 4-task plan is aggressive but achievable for a 2-engineer team in 2 weeks."
}"""

    # Retry messaging templates (from Design Section 2.4)
    RETRY_MESSAGES = {
        "generic_task": """ERROR FEEDBACK FROM LAST ATTEMPT:
Some tasks were too generic or non-actionable. Tasks must be specific with a concrete metric or constraint.

Bad examples: "Fix performance", "Improve database", "Handle edge cases"
Good examples: "Optimize database queries to reduce latency by 50%", "Convert blocking I/O to async/await to handle 10k concurrent connections"

Regenerate the plan with specific, measurable tasks.""",
        "metric_invalid": """ERROR FEEDBACK FROM LAST ATTEMPT:
Some task metrics were malformed or unmeasurable.

Bad metrics: "improve things better", "handle more stuff", "reduce by a bit"
Good metrics: "reduce latency by 50%", "support 10k concurrent requests", "achieve 99.5% uptime"

Ensure every task metric is:
- Quantified (includes a number or percentage)
- Clear (uses standard units: %, ms, seconds, requests/sec, MB, etc.)
- Achievable (realistic for the scope)

Regenerate with valid, measurable metrics.""",
        "vague_mitigation": """ERROR FEEDBACK FROM LAST ATTEMPT:
Some risks had vague or incomplete mitigations. Mitigations must be concrete and actionable.

Bad mitigations: "be careful", "watch out for this", "ensure it works"
Good mitigations: "Use feature flags for gradual rollout; extensive integration test coverage", "Implement scope lock with weekly milestones"

Each mitigation should specify what action to take (e.g., feature flags, testing) and how it reduces the risk.

Regenerate with concrete, actionable mitigations.""",
        "priority_imbalance": """ERROR FEEDBACK FROM LAST ATTEMPT:
Task priorities were unbalanced (too many high-priority tasks). Recalibrate so that:
- No more than 50% of tasks are "high" priority
- At least 1 task is "medium" or "low" priority
- High-priority tasks are truly blocking or on the critical path

Regenerate with a more balanced priority distribution.""",
    }

    @staticmethod
    def build_prompt(
        brief: str, context: dict, retry_count: int = 0, failure_type: Optional[str] = None
    ) -> str:
        """
        Build a rich prompt for Muse Spark 1.3.

        Args:
            brief: Normalized user input brief
            context: Processed optional context dict (may be empty)
            retry_count: 0 for initial, 1-3 for retries
            failure_type: One of "generic_task", "metric_invalid", "vague_mitigation",
                         "priority_imbalance", or None

        Returns:
            Complete prompt string ready for API call

        Reference: Requirement 3 (Generate Structured Plan)
        Reference: Design Section 2.4 (Prompt Template)
        """
        prompt_parts = [PromptConstructor.SYSTEM_ROLE, "", "INPUT BRIEF:", brief, ""]

        # Inject optional context if provided
        if context:
            prompt_parts.append("OPTIONAL CONTEXT:")
            for key, value in context.items():
                # Format context key nicely
                formatted_key = key.replace("_", " ").title()
                prompt_parts.append(f"  {formatted_key}: {value}")
            prompt_parts.append("")

        # Add retry messaging if applicable
        if retry_count > 0 and failure_type and failure_type in PromptConstructor.RETRY_MESSAGES:
            prompt_parts.append(PromptConstructor.RETRY_MESSAGES[failure_type])
            prompt_parts.append("")

        # Add schema specification
        prompt_parts.append("OUTPUT SCHEMA (must output valid JSON matching this exactly):")
        prompt_parts.append(PromptConstructor.SCHEMA_SPECIFICATION)
        prompt_parts.append("")

        # Add example output to anchor model's formatting
        prompt_parts.append("EXAMPLE OUTPUT (demo scenario: microservice 10x scaling):")
        prompt_parts.append(PromptConstructor.DEMO_EXAMPLE_OUTPUT)
        prompt_parts.append("")

        # Final instruction
        prompt_parts.append(
            "Now generate a plan for the input brief. Output ONLY valid JSON, no additional text."
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def get_schema_specification() -> str:
        """Return the JSON schema specification."""
        return PromptConstructor.SCHEMA_SPECIFICATION

    @staticmethod
    def get_system_role() -> str:
        """Return MuseFlow's system role."""
        return PromptConstructor.SYSTEM_ROLE

    @staticmethod
    def get_demo_example() -> str:
        """Return the demo example output."""
        return PromptConstructor.DEMO_EXAMPLE_OUTPUT
