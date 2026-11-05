"""Run all sample briefs and report request latency."""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from museflow.demo_scenarios import (  # noqa: E402
    DEMO_SCENARIOS,
    load_demo_scenario,
)
from museflow.env_loader import load_env  # noqa: E402
from museflow.muse_spark_integration import (  # noqa: E402
    MuseSparkIntegrationError,
)
from museflow.planner_engine import PlannerEngine  # noqa: E402


def run_demo_scenario(scenario_num: int, api_key: str) -> tuple[bool, float]:
    """Run one sample brief and return its outcome and elapsed time."""
    brief, context, name = load_demo_scenario(scenario_num)
    print(f"\n{'=' * 70}")
    print(f"Demo Scenario {scenario_num}: {name}")
    print(f"{'=' * 70}\n")
    print(f"Input Brief: {brief[:80]}...")
    if context:
        print(f"Context: {context}")

    engine = PlannerEngine(api_key, max_retries=3, timeout_seconds=15.0)
    start_time = time.time()
    started_at = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\nStarting at {started_at}...")

    try:
        success, plan, failure, flagged = engine.generate_plan(
            brief, context, verbose=False
        )
    except MuseSparkIntegrationError as exc:
        elapsed = time.time() - start_time
        print(f"\nRequest failed after {elapsed:.2f}s: {exc}")
        return False, elapsed

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f}s (target: <15s)")
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print(f"Retries: {engine.metrics.get('retries', 0)}")

    if success:
        print(f"Summary: {plan.get('summary', 'N/A')}")
        print(f"Tasks: {len(plan.get('tasks', []))}")
        print(f"Risks: {len(plan.get('risks', []))}")
        if flagged:
            print(f"Flagged risks: {len(flagged)} (non-blocking)")
    else:
        print(f"Failure reason: {failure}")

    return success, elapsed


def main() -> int:
    """Run all sample briefs, requiring a configured API key."""
    load_env()
    api_key = os.getenv("META_MODEL_API_KEY")
    if not api_key:
        print(
            "Error: META_MODEL_API_KEY is not set. "
            "Set it in your shell or local .env.",
            file=sys.stderr,
        )
        return 1

    results = [
        run_demo_scenario(scenario_num, api_key)
        for scenario_num in sorted(DEMO_SCENARIOS)
    ]
    successful = sum(success for success, _ in results)
    under_target = sum(elapsed < 15.0 for _, elapsed in results)
    print(f"\nSuccess rate: {successful}/{len(results)}")
    print(f"Under 15 seconds: {under_target}/{len(results)}")
    return 0 if successful == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
