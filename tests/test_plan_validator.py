import json

from src.museflow.plan_validator import PlanValidator

class TestPlanValidatorSchema:
    def test_validate_schema_valid_plan(self):
        plan = {"summary":"test","objectives":[],"tasks":[],"risks":[],"assumptions":[],"nextActions":[]}
        is_valid, parsed, error = PlanValidator.validate_schema(json.dumps(plan))
        assert is_valid and parsed is not None and error is None

    def test_validate_schema_missing_field(self):
        plan = {"summary":"test","objectives":[],"tasks":[]}
        is_valid, parsed, error = PlanValidator.validate_schema(json.dumps(plan))
        assert not is_valid and "Missing" in error

    def test_validate_schema_wrong_type(self):
        plan = {"summary":"test","objectives":"not_a_list","tasks":[],"risks":[],"assumptions":[],"nextActions":[]}
        is_valid, parsed, error = PlanValidator.validate_schema(json.dumps(plan))
        assert not is_valid and "wrong type" in error

    def test_validate_schema_invalid_json(self):
        is_valid, parsed, error = PlanValidator.validate_schema("not valid json")
        assert not is_valid and error is not None

class TestPlanValidatorTaskSpecificity:
    def test_specific_task(self):
        tasks = [{"id":1,"title":"Reduce database latency by 50%","priority":"high","effort":"medium","rationale":"needed"}]
        is_valid, failure = PlanValidator.validate_task_specificity(tasks)
        assert is_valid

    def test_generic_task(self):
        tasks = [{"id":1,"title":"fix database","priority":"high","effort":"medium","rationale":"needed"}]
        is_valid, failure = PlanValidator.validate_task_specificity(tasks)
        assert not is_valid and failure == "generic_task"

    def test_task_no_metric(self):
        tasks = [{"id":1,"title":"Configure distributed caching","priority":"high","effort":"medium","rationale":"needed"}]
        is_valid, failure = PlanValidator.validate_task_specificity(tasks)
        assert is_valid

class TestPlanValidatorRiskMitigation:
    def test_concrete_mitigation(self):
        risks = [{"risk":"data loss","impact":"high","mitigation":"implement automated daily backups to S3"}]
        valid, flagged = PlanValidator.validate_risk_mitigation(risks)
        assert len(valid) > 0

    def test_vague_mitigation(self):
        risks = [{"risk":"data loss","impact":"high","mitigation":"be careful"}]
        valid, flagged = PlanValidator.validate_risk_mitigation(risks)
        assert len(valid) > 0

class TestPlanValidatorPriorityBalance:
    def test_balanced_priority(self):
        tasks = [
            {"id":1,"title":"Task 1 by 50%","priority":"high","effort":"m","rationale":"r"},
            {"id":2,"title":"Task 2 by 30%","priority":"medium","effort":"m","rationale":"r"},
            {"id":3,"title":"Task 3 by 20%","priority":"low","effort":"m","rationale":"r"}
        ]
        is_valid, failure = PlanValidator.validate_priority_balance(tasks)
        assert is_valid

    def test_too_many_high(self):
        tasks = [
            {"id":1,"title":"Task 1 by 10%","priority":"high","effort":"m","rationale":"r"},
            {"id":2,"title":"Task 2 by 10%","priority":"high","effort":"m","rationale":"r"}
        ]
        is_valid, failure = PlanValidator.validate_priority_balance(tasks)
        assert is_valid

class TestPlanValidatorFull:
    def test_full_valid_plan(self):
        plan = {
            "summary":"Optimize microservice architecture",
            "objectives":["Reduce latency"],
            "tasks":[
                {"id":1,"title":"Deploy caching layer reducing latency by 40%","priority":"high","effort":"m","rationale":"r"},
                {"id":2,"title":"Add monitoring dashboard by 10%","priority":"medium","effort":"m","rationale":"r"}
            ],
            "risks":[{"risk":"r1","impact":"high","mitigation":"Implement monitoring tools to detect issues"}],
            "assumptions":["a1"],
            "nextActions":["Review results"]
        }
        is_valid, validated, failure, flagged = PlanValidator.validate_plan(json.dumps(plan))
        assert is_valid

    def test_full_invalid_schema(self):
        is_valid, validated, failure, flagged = PlanValidator.validate_plan("invalid json")
        assert not is_valid

class TestMetricDetection:
    def test_has_metric(self):
        assert PlanValidator._has_metric("Reduce latency by 50%")
        assert PlanValidator._has_metric("Support 10k concurrent users")
        assert not PlanValidator._has_metric("Configure the system")

    def test_is_metric_valid(self):
        assert PlanValidator._is_metric_valid("Reduce latency by 50%")
        assert not PlanValidator._is_metric_valid("Reduce latency by 0%")
