# MuseFlow — Meta Global AI Developer Hackathon

MuseFlow is an AI-powered workflow planner built for the Meta Global AI Developer Hackathon. It uses Meta Muse Spark 1.3 through the Meta Model API to turn a project brief into a structured plan.

## Project

The planner returns objectives, prioritized tasks, risks and mitigations, assumptions, and next actions. Its flow is input validation, prompt construction, model inference, response validation, and plan generation. The implementation is an Alpha/hackathon MVP; generated plans require human review.

## Meta AI integration

The application calls the OpenAI-compatible Meta Model API endpoint with model `muse-spark-1.3`. The configured request uses `reasoning_effort="minimal"`. API timings vary; use only measurements from the actual demo run in any presentation.

## Run the project

Clone and enter the actual repository directory:

```powershell
git clone https://github.com/abdelrazekrizk/museflow-ai-workflow-planner.git
Set-Location museflow-ai-workflow-planner
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e '.[dev,testing]'
```

Configure `META_MODEL_API_KEY` in the active shell or local ignored `.env` file. Then run the latency demo:

```powershell
& .\.venv\Scripts\python.exe examples\demo_latency_test.py
```

For a custom CLI brief, use `--input` (not `--brief`) and supply at least 50 characters, up to 2,000 after trimming:

```powershell
& .\.venv\Scripts\python.exe -m museflow.cli --input 'Our Python microservice handles auth requests and experiences 10x traffic growth during peak hours. Currently, response latency is 500ms p99 and we need to reduce it to under 100ms while supporting 10k concurrent connections. We have 4 engineers, a $50k budget, and 2 weeks.'
```

Run automated tests (API calls are mocked):

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/ -q
```

## Current demo scenarios

1. Microservice scaling for 10x traffic
2. Mobile app redesign and crash-rate reduction
3. API performance degradation investigation

Watch the [MuseFlow demo video](https://youtu.be/stdiOyM0nVs).