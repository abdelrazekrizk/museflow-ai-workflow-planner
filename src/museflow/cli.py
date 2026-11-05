import argparse
import json
import logging
import os
import sys

from .env_loader import load_env
from .planner_engine import PlannerEngine

logger = logging.getLogger(__name__)


class CLIInterface:
    @staticmethod
    def main():
        load_env()
        parser = argparse.ArgumentParser(description="MuseFlow: AI-powered workflow planner")
        parser.add_argument("--input", type=str, help="User brief (50-2000 chars)")
        parser.add_argument("--input-file", type=str, help="Path to file with brief")
        parser.add_argument("--team-size", type=int, help="Team size")
        parser.add_argument("--budget", type=str, help="Budget constraint")
        parser.add_argument("--constraints", type=str, help="Additional constraints")
        parser.add_argument("--architecture-notes", type=str, help="Architecture context")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
        parser.add_argument("--output-file", type=str, help="Path to save JSON output")
        args = parser.parse_args()

        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)

        brief = args.input
        if args.input_file:
            try:
                with open(args.input_file, "r") as f:
                    brief = f.read()
            except Exception as e:
                print(f"Error reading file: {e}", file=sys.stderr)
                return 1

        if not brief:
            print("Error: --input or --input-file required", file=sys.stderr)
            return 1

        context = {}
        if args.team_size:
            context["team_size"] = str(args.team_size)
        if args.budget:
            context["budget"] = args.budget
        if args.constraints:
            context["constraints"] = args.constraints
        if args.architecture_notes:
            context["architecture_notes"] = args.architecture_notes

        api_key = os.getenv("META_MODEL_API_KEY")
        if not api_key:
            print(
                "Error: META_MODEL_API_KEY is not set in the shell or .env.",
                file=sys.stderr,
            )
            return 1

        try:
            engine = PlannerEngine(api_key)
            success, plan, failure_reason, _ = engine.generate_plan(
                brief, context, verbose=args.verbose
            )

            if success:
                output = json.dumps(plan, indent=2)
                if args.output_file:
                    with open(args.output_file, "w") as f:
                        f.write(output)
                    print(f"Plan saved to {args.output_file}")
                else:
                    print(output)
                return 0
            else:
                print(f"Error: {failure_reason}", file=sys.stderr)
                if plan:
                    print(json.dumps(plan, indent=2), file=sys.stderr)
                return 1

        except KeyboardInterrupt:
            print("Interrupted by user", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1


def main():
    return CLIInterface.main()


if __name__ == "__main__":
    sys.exit(main())
