"""Tests for loading local environment configuration safely."""

import os

from src.museflow.env_loader import load_env


def test_load_env_uses_file_when_shell_value_is_missing(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("MUSEFLOW_TEST_SETTING=from-file\n", encoding="utf-8")
    monkeypatch.delenv("MUSEFLOW_TEST_SETTING", raising=False)

    assert load_env(env_file)
    assert os.environ["MUSEFLOW_TEST_SETTING"] == "from-file"


def test_load_env_preserves_existing_shell_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("MUSEFLOW_TEST_SETTING=from-file\n", encoding="utf-8")
    monkeypatch.setenv("MUSEFLOW_TEST_SETTING", "from-shell")

    assert load_env(env_file)
    assert os.environ["MUSEFLOW_TEST_SETTING"] == "from-shell"


def test_load_env_returns_false_when_file_is_missing(tmp_path):
    assert not load_env(tmp_path / "missing.env")
