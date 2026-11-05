# MuseFlow

MuseFlow is an AI-powered workflow planning assistant that transforms ambiguous project briefs and rough requirements into structured, actionable execution plans in seconds.

Built for the **Meta Global AI Developer Hackathon** (Oct 27 – Nov 4, 2026) using **Meta Muse Spark 1.3**.

## What is MuseFlow?

MuseFlow converts vague inputs like:

```txt
"We have a Python microservice that needs to handle 10x more traffic.
Current bottlenecks: database queries and sync I/O. Limited budget.
Need to present to leadership in 2 weeks."
```

Into a structured plan with:

- **Prioritized tasks** (with effort estimates and rationale)
- **Identified risks** (with concrete mitigation strategies)
- **Clear assumptions** (about constraints and team capability)
- **Next actions** (immediate steps to begin work)

## DEMO VIDEO

Watch the [MuseFlow demo video](https://youtu.be/stdiOyM0nVs) for a recording outline.

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/abdelrazekrizk/museflow-ai-workflow-planner.git
cd museflow-ai-workflow-planner
python -m venv .venv
python -m pip install -e ".[dev,testing]"
```

On Windows, run the following in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,testing]"
```

### 2. Configure API Key

```bash
# Optional: copy .env.example to .env and add META_MODEL_API_KEY there.
# A META_MODEL_API_KEY already set in the active shell takes precedence.
```

Get your key from [Meta Model API Dashboard](https://dev.meta.ai/dashboard).

### 3. Run Demo

```bash
python examples/demo.py
```

For request latency details, run `python examples/demo_latency_test.py`.
Both demos use the shell key first and fall back to the project-root `.env`.
The API key is never printed. To submit a custom brief, run this from the
project root after installing the package:

```powershell
python -m museflow.cli --input 'Our Python microservice handles auth requests and experiences 10x traffic growth during peak hours. Currently, response latency is 500ms p99 and we need to reduce it to under 100ms while supporting 10k concurrent connections. We have 4 engineers, a $50k budget, and 2 weeks.'
```

Briefs must contain **50–2,000 characters** after trimming. A short label such
as `Microservice scaling for 10x traffic` is only 36 characters, so the input
validator rejects it. Provide a complete project brief instead.

### Included demo scenarios

- Microservice scaling for 10x traffic
- Mobile app redesign and crash-rate reduction
- API performance degradation investigation

## Features Built During Hackathon

✅ Meta Model API integration (Muse Spark 1.3)
✅ Core planner engine (input → prompt → reasoning → plan)
✅ Schema validation for required JSON fields
✅ Failure-specific retry logic (up to 3 retries after the initial request)
✅ Basic task validation (required fields and selected generic-title checks; metrics are not enforced)
✅ Risk structure validation (non-empty mitigations are accepted; strategy quality requires human review)
✅ Priority presence validation (priority distribution is currently relaxed)
✅ CLI interface for easy demo execution
✅ Live API latency and retry metrics are reported; actual timings vary by run

## Example Output

```json
{
  "summary": "Upgrade microservice for 10x load via async refactor and DB query optimization",
  "objectives": [
    "Support 10x concurrent requests",
    "Reduce database latency by 50%",
    "Maintain backward compatibility"
  ],
  "tasks": [
    {
      "id": 1,
      "title": "Audit database queries to identify bottlenecks using slow query logs",
      "priority": "high",
      "effort": "2 days",
      "rationale": "Database is the stated primary bottleneck"
    },
    ...
  ],
  "risks": [
    {
      "risk": "Breaking changes in async refactor",
      "impact": "high",
      "mitigation": "Use feature flags for gradual rollout; extensive integration tests"
    },
    ...
  ],
  "assumptions": ["Database is the primary bottleneck", "Team has async/await experience"],
  "nextActions": ["Run profiler on production", "Set up load test environment"]
}
```

## Architecture

MuseFlow uses a 6-component architecture:

1. **InputHandler** – Normalize and validate user input
2. **PromptConstructor** – Build rich prompts with context
3. **MuseSparkIntegration** – Call Meta Model API securely
4. **PlanValidator** – Validate output against schema and correctness properties
5. **PlannerEngine** – Orchestrate workflow with retry logic
6. **CLIInterface** – Command-line entry point for demo

## Requirements

- Python 3.14+
- Meta Model API key ($150 hackathon credits provided)
- Internet connection (for API calls)

## Development

Install dev dependencies:

```bash
python -m pip install -e ".[dev,testing]"
```

Run tests:

```bash
python -m pytest tests/ -v --cov
```

Format code:

```bash
black src/
ruff check --fix src/
```

## Project Status

- **Status**: Alpha (Hackathon MVP)
- **Last Updated**: Nov 2026
- **Team**: MuseFlow Hackathon Contributors
- **Contributors**: [Abdelrazek Rizk](https://www.linkedin.com/in/abdelrazek-rizk/) and [Sherine Rizk](https://www.linkedin.com/in/sherine-rizk/)

## License

MIT License — see [LICENSE](LICENSE) for details.

## Support

For questions or issues, create an [issue on GitHub](https://github.com/abdelrazekrizk/museflow-ai-workflow-planner/issues).

---

Built for the Meta Global AI Developer Hackathon.
