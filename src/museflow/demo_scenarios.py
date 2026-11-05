"""Sample briefs used by the interactive demos."""

from typing import Dict, Tuple

DEMO_SCENARIOS: Dict[int, Tuple[str, Dict[str, str], str]] = {
    1: (
        "Our Python microservice handles auth requests and experiences "
        "10x traffic growth during peak hours. Currently, response latency is "
        "500ms p99 and we need to reduce it to under 100ms while supporting "
        "10k concurrent connections. We have 4 engineers, a $50k budget, "
        "and 2 weeks.",
        {
            "team_size": "4",
            "budget": "$50k",
            "constraints": "2 weeks",
            "architecture_notes": ("Currently single node, needs horizontal scaling"),
        },
        "Microservice 10x Scaling",
    ),
    2: (
        "Mobile app needs redesign for better UX. Current app has low "
        "retention and high crash rates. Team of 3, budget $30k, "
        "with a 3-week timeline.",
        {"team_size": "3", "budget": "$30k", "constraints": "3 weeks"},
        "Mobile App Redesign",
    ),
    3: (
        "API response time increased 3x in the past month despite unchanged "
        "traffic patterns. The infrastructure team reports high CPU usage "
        "on backend servers.",
        {},
        "API Performance Degradation",
    ),
}


def load_demo_scenario(scenario_num: int) -> Tuple[str, Dict[str, str], str]:
    """Return the brief, context, and display name for a demo scenario."""
    try:
        return DEMO_SCENARIOS[scenario_num]
    except KeyError as exc:
        raise ValueError(f"Unknown demo scenario: {scenario_num}") from exc
