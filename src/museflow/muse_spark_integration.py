"""MuseSparkIntegration: Secure client for Meta Model API (Muse Spark 1.3)."""

import hashlib
import logging
import time
from typing import Tuple, Optional, Dict, Any
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class MuseSparkIntegrationError(Exception):
    """Custom exception for MuseSparkIntegration errors."""

    pass


class MuseSparkIntegration:
    """Secure wrapper around Meta Model API (Muse Spark 1.3)."""

    MODEL_ID = "muse-spark-1.3"
    API_BASE_URL = "https://api.meta.ai/v1"
    API_TIMEOUT = 25.0
    MAX_TOKENS = 2048  # Reduced from 4096 for faster response

    def __init__(self, api_key: str):
        """Initialize Meta Model API client."""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        self.client = OpenAI(
            base_url=self.API_BASE_URL,
            api_key=api_key,
            timeout=self.API_TIMEOUT,
        )

        self.api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:8]

    def call(
        self, prompt: str, reasoning_effort: str = "minimal"  # Explicit minimal for latency
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """Call Muse Spark 1.3 with a prompt."""
        start_time = time.time()

        try:
            logger.debug(
                f"[{self.api_key_hash}] Calling Muse Spark 1.3 with reasoning_effort={reasoning_effort}"
            )

            # Use chat.completions.create with explicit parameters from Meta docs
            # Developer message for better control (preferred over system)
            response = self.client.chat.completions.create(
                model=self.MODEL_ID,
                max_tokens=self.MAX_TOKENS,  # Reduced to 2048 for speed
                temperature=1.0,  # Meta default
                reasoning_effort=reasoning_effort,  # Explicit minimal
                messages=[
                    {
                        "role": "developer",
                        "content": "You are a workflow planning assistant. Generate clear, actionable execution plans in valid JSON format. Be specific with metrics and concrete steps.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            # Extract response text
            response_text = response.choices[0].message.content if response.choices else ""

            if not response_text:
                raise MuseSparkIntegrationError("API returned empty response")

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            tokens_used = (
                response.usage.total_tokens if hasattr(response, "usage") and response.usage else 0
            )

            # Track reasoning tokens if available
            reasoning_tokens = 0
            if hasattr(response, "usage") and response.usage:
                if hasattr(response.usage, "completion_tokens_details"):
                    reasoning_tokens = (
                        response.usage.completion_tokens_details.reasoning_tokens
                        if hasattr(response.usage.completion_tokens_details, "reasoning_tokens")
                        else 0
                    )

            metrics = {
                "api_latency_ms": latency_ms,
                "tokens_used": tokens_used,
                "reasoning_tokens": reasoning_tokens,
                "model": self.MODEL_ID,
                "reasoning_effort": reasoning_effort,
            }

            logger.info(
                f"[{self.api_key_hash}] API succeeded in {latency_ms:.0f}ms ({tokens_used} tokens, {reasoning_tokens} reasoning)"
            )

            return (response_text, None, metrics)

        except AuthenticationError as e:
            msg = "API authentication failed (401). Check META_MODEL_API_KEY."
            logger.error(msg)
            raise MuseSparkIntegrationError(msg) from e
        except RateLimitError as e:
            msg = "API rate limited (429). Retry with backoff."
            logger.warning(msg)
            raise MuseSparkIntegrationError(msg) from e
        except APITimeoutError as e:
            msg = f"API timeout (exceeded {self.API_TIMEOUT}s)"
            logger.error(msg)
            raise MuseSparkIntegrationError(msg) from e
        except APIError as e:
            msg = f"API error: {str(e)[:100]}"
            logger.error(msg)
            raise MuseSparkIntegrationError(msg) from e
        except MuseSparkIntegrationError:
            raise
        except Exception as e:
            msg = f"Unexpected error: {str(e)[:100]}"
            logger.error(msg)
            raise MuseSparkIntegrationError(msg) from e
