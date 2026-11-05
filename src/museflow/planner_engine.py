import logging
import random
import time
from typing import Dict, List, Optional, Tuple
from .input_handler import InputHandler
from .prompt_constructor import PromptConstructor
from .muse_spark_integration import MuseSparkIntegration, MuseSparkIntegrationError
from .plan_validator import PlanValidator

logger = logging.getLogger(__name__)


class PlannerEngine:
    def __init__(self, api_key: str, max_retries: int = 3, timeout_seconds: float = 15.0):
        if not api_key:
            raise ValueError("api_key cannot be empty")
        self.input_handler = InputHandler()
        self.prompt_constructor = PromptConstructor()
        self.muse_spark = MuseSparkIntegration(api_key)
        self.plan_validator = PlanValidator()
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.metrics = {}

    @staticmethod
    def _calculate_backoff(retry_attempt: int) -> float:
        base_delay = 2**retry_attempt
        jitter = random.uniform(0, base_delay * 0.1)
        return base_delay + jitter

    def _wait_with_backoff(self, retry_attempt: int) -> None:
        delay = self._calculate_backoff(retry_attempt)
        logger.debug(f"Waiting {delay:.2f}s before retry")
        time.sleep(delay)

    def _should_retry(
        self, failure_type: Optional[str], retry_count: int, elapsed_time: float
    ) -> bool:
        if retry_count >= self.max_retries or elapsed_time >= self.timeout_seconds:
            return False
        retry_types = [
            "schema_error",
            "JSON parse error",
            "api_error",
            "timeout",
            "generic_task",
            "metric_invalid",
            "priority_imbalance",
        ]
        return failure_type in retry_types

    def generate_plan(
        self, brief: str, context: Optional[Dict[str, str]] = None, verbose: bool = False
    ) -> Tuple[bool, Optional[Dict], Optional[str], List[Dict]]:
        self.start_time = time.time()
        self.metrics = {"retries": 0, "tokens_used": 0}
        if verbose:
            logger.setLevel(logging.DEBUG)
        logger.info("Starting plan generation")
        try:
            normalized_brief, processed_context = self.input_handler.normalize(brief, context)
            logger.debug(f"Normalized brief: {len(normalized_brief)} chars")
        except ValueError as e:
            logger.error(f"Input validation failed: {str(e)}")
            return (False, None, f"Input error: {str(e)}", [])
        retry_count, best_plan, best_validation_result, failure_reason = 0, None, None, None
        while retry_count <= self.max_retries:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.timeout_seconds:
                break
            if retry_count > 0:
                self._wait_with_backoff(retry_count - 1)
            try:
                failure_type = best_validation_result[2] if best_validation_result else None
                prompt = self.prompt_constructor.build_prompt(
                    normalized_brief, processed_context, retry_count, failure_type
                )
                response_json, reasoning, call_metrics = self.muse_spark.call(prompt)
                self.metrics["tokens_used"] = call_metrics.get("tokens_used", 0)
                is_valid, plan_dict, validation_failure_type, flagged_risks = (
                    self.plan_validator.validate_plan(response_json, brief=normalized_brief)
                )
                best_validation_result = (
                    is_valid,
                    plan_dict,
                    validation_failure_type,
                    flagged_risks,
                )
                best_plan = plan_dict
                if is_valid:
                    elapsed_time = time.time() - self.start_time
                    logger.info(f"Plan generation succeeded in {elapsed_time:.2f}s")
                    self.metrics["retries"], self.metrics["latency_ms"] = (
                        retry_count,
                        elapsed_time * 1000,
                    )
                    return (True, plan_dict, None, flagged_risks)
                failure_reason = validation_failure_type
                if not self._should_retry(validation_failure_type, retry_count, elapsed_time):
                    return (False, plan_dict, validation_failure_type, flagged_risks)
                retry_count += 1
            except MuseSparkIntegrationError as e:
                logger.error(f"API error: {str(e)}")
                elapsed_time = time.time() - self.start_time
                if not self._should_retry("api_error", retry_count, elapsed_time):
                    return (False, best_plan, "api_error", [])
                retry_count += 1
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return (False, best_plan, "unexpected_error", [])
        elapsed_time = time.time() - self.start_time
        self.metrics["retries"], self.metrics["latency_ms"] = retry_count, elapsed_time * 1000
        if best_validation_result:
            _, plan_dict, failure_type, flagged_risks = best_validation_result
            return (False, plan_dict, failure_type, flagged_risks)
        return (False, None, failure_reason or "max_retries_exhausted", [])
