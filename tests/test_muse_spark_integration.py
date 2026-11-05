"""Tests for MuseSparkIntegration component."""

import pytest
from unittest.mock import MagicMock, patch
from src.museflow.muse_spark_integration import MuseSparkIntegration, MuseSparkIntegrationError


class TestMuseSparkIntegrationInit:
    """Test initialization."""

    def test_init_with_valid_key(self):
        """Initialization with valid API key succeeds."""
        integration = MuseSparkIntegration("test-key-123")
        assert integration.api_key_hash is not None
        assert len(integration.api_key_hash) == 8

    def test_init_with_empty_key_raises_error(self):
        """Initialization with empty API key raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            MuseSparkIntegration("")


class TestMuseSparkIntegrationCall:
    """Test API call handling."""

    @patch("src.museflow.muse_spark_integration.OpenAI")
    def test_call_success(self, mock_openai_class):
        """Successful API call returns (response_json, reasoning, metrics)."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the chat.completions.create response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '{"summary": "test plan"}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_response.usage.total_tokens = 150
        mock_client.chat.completions.create.return_value = mock_response

        integration = MuseSparkIntegration("test-key")
        response_json, reasoning, metrics = integration.call("test prompt")

        assert response_json == '{"summary": "test plan"}'
        assert metrics["tokens_used"] == 150
        assert "api_latency_ms" in metrics

    @patch("src.museflow.muse_spark_integration.OpenAI")
    def test_call_with_reasoning(self, mock_openai_class):
        """API call with reasoning included."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '{"tasks": []}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_response.usage.total_tokens = 300
        mock_response.usage.completion_tokens_details = MagicMock(reasoning_tokens=100)
        mock_client.chat.completions.create.return_value = mock_response

        integration = MuseSparkIntegration("test-key")
        response_json, reasoning, metrics = integration.call("test prompt")

        assert response_json == '{"tasks": []}'
        assert metrics["reasoning_tokens"] == 100

    @patch("src.museflow.muse_spark_integration.OpenAI")
    def test_call_auth_error(self, mock_openai_class):
        """API authentication error raises MuseSparkIntegrationError."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        # Use a generic exception that will be caught as APIError
        mock_client.chat.completions.create.side_effect = Exception("401 Unauthorized")

        integration = MuseSparkIntegration("bad-key")

        with pytest.raises(MuseSparkIntegrationError):
            integration.call("test prompt")

    @patch("src.museflow.muse_spark_integration.OpenAI")
    def test_call_empty_response(self, mock_openai_class):
        """Empty API response raises MuseSparkIntegrationError."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = ""
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_response.usage.total_tokens = 10
        mock_client.chat.completions.create.return_value = mock_response

        integration = MuseSparkIntegration("test-key")

        with pytest.raises(MuseSparkIntegrationError, match="empty"):
            integration.call("test prompt")


class TestMuseSparkIntegrationConstants:
    """Test component constants."""

    def test_model_constants(self):
        """Component defines correct API constants."""
        assert MuseSparkIntegration.MODEL_ID == "muse-spark-1.3"
        assert MuseSparkIntegration.API_BASE_URL == "https://api.meta.ai/v1"
        assert MuseSparkIntegration.API_TIMEOUT == 25.0
