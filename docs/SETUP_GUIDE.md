# MuseFlow Setup Guide

## Requirements

- Windows PowerShell
- Python 3.14 or newer
- A Meta Model API key to run live demos (unit tests use mocked API calls)

## Install

From the MuseFlow project directory, create and populate the local virtual environment:

```powershell
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -e '.[dev,testing]'
```

`pyproject.toml` is the standard package metadata file. No temporary rename is needed.

## Configure credentials

You can set `META_MODEL_API_KEY` in the active PowerShell session:

```powershell
$env:META_MODEL_API_KEY = 'your-key'
```

Or copy `.env.example` to `.env` and add your key there. The project-root `.env` is ignored by git. If both are set, the active shell value wins; `.env` only fills a missing value. The application and tests do not print the credential.

## Run tests

```powershell
New-Item -ItemType Directory -Force -Path 'test-results' | Out-Null
& .\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short 2>&1 |
    Set-Content -Path 'test-results\test-output.txt'
Get-Content 'test-results\test-output.txt' | Select-Object -Last 20
```

Tests are mocked and do not require a live API key. `tests/conftest.py` loads a local `.env` for optional integration workflows, without overriding active shell variables.

## Run demos

From the project directory, use:

```powershell
& .\.venv\Scripts\python.exe examples\demo.py
& .\.venv\Scripts\python.exe examples\demo_latency_test.py
```

Both demos require a key, load `.env` as a fallback, and prefer the active shell key. They make live API requests and may incur usage charges. A missing key produces a clear setup error before any request is made.

## Troubleshooting

- **`No module named dotenv`**: install the declared project dependencies with `python.exe -m pip install -e '.[dev,testing]'` using the `.venv` interpreter.
- **Missing-key error**: set `META_MODEL_API_KEY` in the shell or the ignored project-root `.env` file.
- **Pytest collection or package errors**: verify that `pyproject.toml` exists and rerun the editable install above; do not rename the metadata file.
- **API authentication/network errors**: check the key through the provider dashboard and verify internet connectivity. No live API check is part of the unit-test suite.
