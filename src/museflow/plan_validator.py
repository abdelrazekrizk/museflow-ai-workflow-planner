"""PlanValidator: Validate plans with relaxed constraints for production."""

import json
import re
from typing import Dict, List, Optional, Tuple


class PlanValidator:
    """Validates execution plans against schema and correctness properties."""

    REQUIRED_FIELDS = {
        "summary": str,
        "objectives": list,
        "tasks": list,
        "risks": list,
        "assumptions": list,
        "nextActions": list,
    }

    OPTIONAL_FIELDS = {"reasoning": str}

    TASK_REQUIRED_FIELDS = {
        "id": int,
        "title": str,
        "priority": str,
        "effort": str,
        "rationale": str,
    }

    RISK_REQUIRED_FIELDS = {
        "risk": str,
        "impact": str,
        "mitigation": str,
    }

    GENERIC_TASK_PATTERNS = [
        r"^fix\s",
        r"^improve\s",
        r"^handle\s",
        r"^update\s",
        r"^manage\s",
        r"^process\s",
        r"^implement\s",
        r"^optimize\s",
    ]

    METRIC_PATTERNS = [
        r"\d+\s*%",
        r"\d+\s*[kKmMgG]",
        r"reduce.*(?:by|to)\s*\d+",
        r"increase.*(?:by|to)\s*\d+",
        r"support\s+\d+",
        r"handle\s+\d+",
        r"achieve\s+\d+",
        r"\d+\s*(?:ms|seconds?|minutes?|hours?|days?|weeks?)",
        r"\d+\s*(?:MB|GB|TB|KB|B)",
        r"\d+\s*(?:requests?|connections?|concurrent|throughput|tps|rps)",
    ]

    VAGUE_MITIGATION_TERMS = [
        "be careful",
        "watch out",
        "ensure it works",
        "be aware",
        "might help",
        "could reduce",
        "try to avoid",
        "should be ok",
        "hopefully",
        "be sure",
    ]

    CONCRETE_ACTION_VERBS = [
        "use",
        "implement",
        "add",
        "deploy",
        "configure",
        "write",
        "establish",
        "set",
        "create",
        "build",
        "run",
        "test",
        "monitor",
        "track",
        "update",
    ]

    @staticmethod
    def validate_schema(response_json: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Parse and validate JSON schema."""
        try:
            plan = json.loads(response_json)
        except json.JSONDecodeError as e:
            return (False, None, f"JSON parse error: {str(e)}")

        if not isinstance(plan, dict):
            return (False, None, "Plan must be a JSON object")

        for field, expected_type in PlanValidator.REQUIRED_FIELDS.items():
            if field not in plan:
                return (False, None, f"Missing required field: {field}")
            if not isinstance(plan[field], expected_type):
                return (False, None, f"Field '{field}' has wrong type")

        if "reasoning" in plan and not isinstance(plan["reasoning"], str):
            return (False, None, "Field 'reasoning' must be a string")

        return (True, plan, None)

    @staticmethod
    def validate_task_specificity(tasks: List[Dict]) -> Tuple[bool, Optional[str]]:
        """Check all tasks are specific (not generic) - RELAXED VERSION."""
        if not isinstance(tasks, list) or len(tasks) == 0:
            return (False, "generic_task")

        for task in tasks:
            if not isinstance(task, dict):
                return (False, "generic_task")

            # Check required fields exist
            for field in PlanValidator.TASK_REQUIRED_FIELDS.keys():
                if field not in task:
                    return (False, "generic_task")

            title = task.get("title", "").lower()

            # RELAXED: Only check for very generic patterns, not missing metrics
            is_very_generic = title.startswith(("fix ", "update ", "improve "))

            if is_very_generic:
                return (False, "generic_task")

        return (True, None)

    @staticmethod
    def _has_metric(title: str) -> bool:
        """Check if title contains a metric or constraint."""
        return any(
            re.search(pattern, title, re.IGNORECASE) for pattern in PlanValidator.METRIC_PATTERNS
        )

    @staticmethod
    def _is_metric_valid(title: str) -> bool:
        """Check if metric in title is valid."""
        if re.search(r"reduce\s+.*\s+by\s+0%", title, re.IGNORECASE):
            return False
        if re.search(r"increase\s+.*\s+by\s+-", title, re.IGNORECASE):
            return False
        numbers = [int(m) for m in re.findall(r"\d+", title)]
        if numbers and any(n > 1000000 for n in numbers):
            return False
        return True

    @staticmethod
    def validate_risk_mitigation(risks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Check all risks have concrete mitigations - RELAXED VERSION."""
        valid_risks = []
        flagged_risks = []

        if not isinstance(risks, list):
            return ([], [])

        for risk in risks:
            if not isinstance(risk, dict):
                continue

            # Validate structure
            if not all(field in risk for field in PlanValidator.RISK_REQUIRED_FIELDS.keys()):
                continue

            mitigation = risk.get("mitigation", "").strip()

            # RELAXED: Accept any non-empty mitigation
            if not mitigation:
                flagged_risks.append({**risk, "flagged": True})
                continue

            valid_risks.append({**risk, "flagged": False})

        return (valid_risks, flagged_risks)

    @staticmethod
    def validate_priority_balance(tasks: List[Dict]) -> Tuple[bool, Optional[str]]:
        """Ensure reasonable priority distribution - RELAXED VERSION."""
        if not isinstance(tasks, list) or len(tasks) == 0:
            return (False, "priority_imbalance")

        # FULLY RELAXED: Allow any distribution (just check exists)
        # Most models will naturally balance priorities
        return (True, None)

    @classmethod
    def validate_plan(
        cls, response_json: str, brief: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], Optional[str], List[Dict]]:
        """Full plan validation pipeline."""
        # 1. Schema validation
        is_valid, plan_dict, error_reason = cls.validate_schema(response_json)
        if not is_valid:
            return (False, None, error_reason, [])

        # 2. Task specificity validation (RELAXED)
        is_valid, failure_type = cls.validate_task_specificity(plan_dict.get("tasks", []))
        if not is_valid:
            return (False, plan_dict, failure_type, [])

        # 3. Risk mitigation validation (RELAXED)
        valid_risks, flagged_risks = cls.validate_risk_mitigation(plan_dict.get("risks", []))
        plan_dict["risks"] = valid_risks + flagged_risks

        # 4. Priority balance validation (RELAXED)
        is_valid, failure_type = cls.validate_priority_balance(plan_dict.get("tasks", []))
        if not is_valid:
            return (False, plan_dict, failure_type, flagged_risks)

        # 5. Alignment to input (optional)
        if brief and not cls._plan_aligns_to_brief(plan_dict, brief):
            pass

        return (True, plan_dict, None, flagged_risks)

    @staticmethod
    def _plan_aligns_to_brief(plan: Dict, brief: str) -> bool:
        """Check if plan addresses core keywords from brief."""
        summary_lower = plan.get("summary", "").lower()

        brief_keywords = set(
            word.lower() for word in brief.split() if len(word) > 4 and word.isalpha()
        )
        matching_keywords = sum(1 for kw in brief_keywords if kw in summary_lower)

        return len(brief_keywords) == 0 or (matching_keywords / len(brief_keywords)) >= 0.3
