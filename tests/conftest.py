"""Pytest configuration and fixtures - auto-load .env variables."""

import os

from src.museflow.env_loader import load_env

# Load .env file before any tests run
load_env()

# Verify critical env vars for integration tests
def pytest_configure(config):
    """Called after command line options are parsed."""
    api_key = os.getenv("META_MODEL_API_KEY")
    if not api_key:
        print("\nWARNING: META_MODEL_API_KEY not set; live demos need a key.")
        print("   Set it to run integration tests with real API")
    else:
        print("\nEnvironment configured; credential value is not displayed.")
