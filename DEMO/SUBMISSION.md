# MuseFlow — Hackathon Submission Summary

**Project:** MuseFlow — AI workflow planner
**Model:** Meta Muse Spark 1.3 through the Meta Model API
**Repository:** [museflow-ai-workflow-planner](https://github.com/abdelrazekrizk/museflow-ai-workflow-planner)

## Summary

MuseFlow turns a project brief into a structured execution plan with objectives, prioritized tasks, risks and mitigations, assumptions, and next actions. It is an early hackathon prototype; generated plans should be reviewed by the project team before use.

## How it works

The Python application validates and normalizes a brief, constructs a model prompt, calls the Meta Model API, validates the response, and returns a plan. The project is organized into six components: `InputHandler`, `PromptConstructor`, `MuseSparkIntegration`, `PlanValidator`, `PlannerEngine`, and `CLIInterface`.

The CLI accepts `--input` or `--input-file`. A brief must contain **50–2,000 characters** after trimming. Short labels are not valid briefs. For example, `Microservice scaling for 10x traffic` is 36 characters and is rejected; use a complete brief such as the microservice scenario in the README.

## Meta Model API use

MuseFlow calls the Meta Model API with the `muse-spark-1.3` model through the OpenAI-compatible client. It requests `reasoning_effort="minimal"` and reports request metrics. Live latency depends on API and network conditions, so any timing shown in a demo should be measured in that recording rather than stated as a guarantee.

## Verification

- **Unit tests:** 58 passed in the last local run on November 4, 2026. Re-run before final submission and update this count if it changes.
- **Lint:** `ruff check .` passed in the project environment.
- Unit tests mock API calls; they do not prove live API availability. The live demo is a separate check and requires a valid API key.

## Run locally

From the repository root, install the project and configure `META_MODEL_API_KEY` in the active environment or the ignored local `.env` file. Then run the demo or the test suite as described in the README and setup guide. The active shell credential takes precedence over `.env`; credentials are not included in the repository.

## Scope and limitations

MuseFlow is an Alpha/hackathon MVP, not a production-ready service. Its API behavior, response quality, and latency should be verified in the target environment. Do not treat generated plans or sample output as guaranteed results.
