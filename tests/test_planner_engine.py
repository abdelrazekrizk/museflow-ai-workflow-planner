import json
import pytest
from unittest.mock import Mock, patch
from src.museflow.planner_engine import PlannerEngine

class TestPlannerEngineInit:
    def test_init_valid_key(self):
        engine = PlannerEngine("test-key")
        assert engine.max_retries == 3
        assert engine.timeout_seconds == 15.0

    def test_init_empty_key(self):
        with pytest.raises(ValueError):
            PlannerEngine("")

class TestBackoffCalculation:
    def test_calculate_backoff_values(self):
        delays = [PlannerEngine._calculate_backoff(i) for i in range(3)]
        assert delays[0] >= 1.0 and delays[0] < 1.1
        assert delays[1] >= 2.0 and delays[1] < 2.2
        assert delays[2] >= 4.0 and delays[2] < 4.4

class TestShouldRetry:
    def test_should_retry_schema_error(self):
        engine = PlannerEngine("test-key")
        assert engine._should_retry("schema_error", 0, 5.0)

    def test_should_retry_max_retries_exhausted(self):
        engine = PlannerEngine("test-key", max_retries=2)
        assert not engine._should_retry("schema_error", 2, 5.0)

    def test_should_retry_timeout_reached(self):
        engine = PlannerEngine("test-key", timeout_seconds=10.0)
        assert not engine._should_retry("schema_error", 0, 15.0)

class TestGeneratePlanMocked:
    @patch("src.museflow.planner_engine.MuseSparkIntegration")
    @patch("src.museflow.planner_engine.InputHandler")
    @patch("src.museflow.planner_engine.PromptConstructor")
    @patch("src.museflow.planner_engine.PlanValidator")
    def test_generate_plan_success_first_try(self, mock_val, mock_prompt, mock_input, mock_spark):
        mock_input_inst = Mock()
        mock_input.return_value = mock_input_inst
        mock_input_inst.normalize.return_value = ("brief 50 chars plus more", {})

        mock_prompt_inst = Mock()
        mock_prompt.return_value = mock_prompt_inst
        mock_prompt_inst.build_prompt.return_value = "test prompt"

        mock_spark_inst = Mock()
        mock_spark.return_value = mock_spark_inst
        plan_json = json.dumps({"summary":"Plan","objectives":[],"tasks":[],"risks":[],"assumptions":[],"nextActions":[]})
        mock_spark_inst.call.return_value = (plan_json, None, {"tokens_used":100})

        mock_val_inst = Mock()
        mock_val.return_value = mock_val_inst
        mock_val_inst.validate_plan.return_value = (True, json.loads(plan_json), None, [])

        engine = PlannerEngine("test-key")
        success, plan, failure, flagged = engine.generate_plan("brief " * 10)

        assert success
        assert plan is not None
        assert failure is None

    @patch("src.museflow.planner_engine.MuseSparkIntegration")
    @patch("src.museflow.planner_engine.InputHandler")
    def test_generate_plan_input_error(self, mock_input, mock_spark):
        mock_input_inst = Mock()
        mock_input.return_value = mock_input_inst
        mock_input_inst.normalize.side_effect = ValueError("Too short")

        engine = PlannerEngine("test-key")
        success, plan, failure, flagged = engine.generate_plan("x")

        assert not success
        assert "Input error" in failure

class TestLatencyMeasurement:
    @patch("src.museflow.planner_engine.MuseSparkIntegration")
    @patch("src.museflow.planner_engine.InputHandler")
    @patch("src.museflow.planner_engine.PromptConstructor")
    @patch("src.museflow.planner_engine.PlanValidator")
    def test_latency_recorded(self, mock_val, mock_prompt, mock_input, mock_spark):
        mock_input_inst = Mock()
        mock_input.return_value = mock_input_inst
        mock_input_inst.normalize.return_value = ("brief " * 10, {})

        mock_prompt_inst = Mock()
        mock_prompt.return_value = mock_prompt_inst
        mock_prompt_inst.build_prompt.return_value = "test"

        mock_spark_inst = Mock()
        mock_spark.return_value = mock_spark_inst
        plan_json = json.dumps({"summary":"P","objectives":[],"tasks":[],"risks":[],"assumptions":[],"nextActions":[]})
        mock_spark_inst.call.return_value = (plan_json, None, {"tokens_used":50})

        mock_val_inst = Mock()
        mock_val.return_value = mock_val_inst
        mock_val_inst.validate_plan.return_value = (True, json.loads(plan_json), None, [])

        engine = PlannerEngine("test-key")
        success, plan, _, _ = engine.generate_plan("brief " * 10)

        assert success
        assert engine.metrics["latency_ms"] > 0
        assert engine.metrics["retries"] == 0
