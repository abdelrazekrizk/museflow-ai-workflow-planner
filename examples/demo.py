import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from museflow.demo_scenarios import load_demo_scenario  # noqa: E402
from museflow.env_loader import load_env  # noqa: E402
from museflow.planner_engine import PlannerEngine  # noqa: E402


def main() -> int:
    """Run each sample brief through MuseFlow."""
    load_env()
    api_key = os.getenv("META_MODEL_API_KEY")
    if not api_key:
        print(
            "Error: META_MODEL_API_KEY is not set. "
            "Set it in your shell or local .env.",
            file=sys.stderr,
        )
        return 1

    for scenario_num in (1, 2, 3):
        brief, context, name = load_demo_scenario(scenario_num)
        print(f"\n{'=' * 60}")
        print(f"Demo Scenario {scenario_num}: {name}")
        print(f"{'=' * 60}\n")
        print(f"Brief: {brief[:100]}...")
        if context:
            print(f"Context: {context}")

        engine = PlannerEngine(api_key, timeout_seconds=15.0)
        success, plan, failure, _ = engine.generate_plan(
            brief, context, verbose=False
        )

        if success:
            print("\nPlan generated successfully!")
            print(f"Summary: {plan.get('summary', 'N/A')}")
            print(f"Tasks: {len(plan.get('tasks', []))} identified")
            print(f"Latency: {engine.metrics.get('latency_ms', 'N/A'):.0f}ms")
            print(f"Retries: {engine.metrics.get('retries', 0)}")
        else:
            print(f"\nFailed to generate plan: {failure}")
            if plan:
                print(
                    "Partial plan available with "
                    f"{len(plan.get('tasks', []))} tasks"
                )

    print(f"\n{'=' * 60}")
    print("Demo complete!")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
