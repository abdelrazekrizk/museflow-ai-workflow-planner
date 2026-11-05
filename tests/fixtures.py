DEMO_INPUT_1 = "Our Python microservice handles authentication requests but experiences 10x traffic growth during peak hours. Currently, response latency is 500ms p99 and we need to reduce it to under 100ms while supporting 10k concurrent connections. We have 4 engineers, budget of $50k, and 2 weeks."

DEMO_CONTEXT_1 = {
    "team_size": "4",
    "budget": "$50k",
    "constraints": "2 weeks",
    "architecture_notes": "Currently single node, needs horizontal scaling"
}

EXPECTED_PLAN_1 = {
    "summary": "Scale Python microservice to handle 10x traffic with sub-100ms latency",
    "objectives": [
        "Reduce p99 latency from 500ms to <100ms",
        "Support 10k concurrent connections",
        "Achieve horizontal scalability"
    ],
    "tasks": [
        {
            "id": 1,
            "title": "Implement connection pooling to reduce by 40% latency",
            "priority": "high",
            "effort": "medium",
            "rationale": "Quick win for latency improvement"
        },
        {
            "id": 2,
            "title": "Deploy load balancer to handle 10k concurrent users",
            "priority": "high",
            "effort": "medium",
            "rationale": "Essential for distributed load"
        },
        {
            "id": 3,
            "title": "Add Redis caching to reduce database calls by 60%",
            "priority": "medium",
            "effort": "medium",
            "rationale": "Improve overall throughput"
        },
        {
            "id": 4,
            "title": "Setup monitoring to track p99 latency metrics",
            "priority": "medium",
            "effort": "small",
            "rationale": "Visibility for improvement validation"
        }
    ],
    "risks": [
        {
            "risk": "Cache invalidation issues with distributed system",
            "impact": "high",
            "mitigation": "Implement TTL-based cache strategy with event-driven updates"
        },
        {
            "risk": "Database connection limit at scale",
            "impact": "high",
            "mitigation": "Deploy connection pool middleware between load balancer and DB"
        },
        {
            "risk": "Network saturation during peak",
            "impact": "medium",
            "mitigation": "Add rate limiting and implement request prioritization"
        }
    ],
    "assumptions": [
        "Infrastructure team can provision additional servers",
        "Current code supports stateless design",
        "Database can handle increased connections"
    ],
    "nextActions": [
        "Implement connection pooling (1 week)",
        "Deploy load balancer (2-3 days)",
        "Add caching layer (3-4 days)",
        "Load testing and optimization"
    ]
}

DEMO_INPUT_2 = "Mobile app needs redesign for better UX. Current app has low retention and high crash rates. Team of 3, budget 30k, 3 weeks timeline."

DEMO_CONTEXT_2 = {
    "team_size": "3",
    "budget": "$30k",
    "constraints": "3 weeks"
}

EXPECTED_PLAN_2 = {
    "summary": "Redesign mobile app to improve UX and reduce crash rate by 80%",
    "objectives": [
        "Improve user retention by 30%",
        "Reduce crash rate to <1%",
        "Enhance UX based on user feedback"
    ],
    "tasks": [
        {
            "id": 1,
            "title": "Conduct user research to identify 5 key pain points",
            "priority": "high",
            "effort": "small",
            "rationale": "Data-driven decision making"
        },
        {
            "id": 2,
            "title": "Refactor core navigation reducing complexity by 40%",
            "priority": "high",
            "effort": "medium",
            "rationale": "Critical for UX improvement"
        },
        {
            "id": 3,
            "title": "Fix stability issues to achieve 99% crash-free rate",
            "priority": "high",
            "effort": "medium",
            "rationale": "Essential for retention"
        }
    ],
    "risks": [
        {
            "risk": "Incomplete migration causing regression",
            "impact": "high",
            "mitigation": "Implement comprehensive automated test suite before release"
        },
        {
            "risk": "User adoption of new interface",
            "impact": "medium",
            "mitigation": "Release phased rollout with in-app tutorials and support"
        }
    ],
    "assumptions": [
        "Users will accept new interface",
        "Team skilled in mobile dev",
        "App stores allow phased rollout"
    ],
    "nextActions": [
        "User research (1 week)",
        "Prototype testing (1 week)",
        "Implementation (1 week)"
    ]
}

DEMO_INPUT_3 = "API experiencing performance degradation. Response time increased 3x in past month with same traffic patterns. Infrastructure team reports high CPU usage on backend servers."

DEMO_CONTEXT_3 = {}

EXPECTED_PLAN_3 = {
    "summary": "Diagnose and fix API performance degradation reducing response time by 3x",
    "objectives": [
        "Reduce response time back to baseline",
        "Identify root cause of CPU spike",
        "Implement preventive measures"
    ],
    "tasks": [
        {
            "id": 1,
            "title": "Analyze logs to identify 3x bottleneck in query performance",
            "priority": "high",
            "effort": "small",
            "rationale": "Urgent diagnosis needed"
        },
        {
            "id": 2,
            "title": "Optimize slow queries reducing CPU by 50%",
            "priority": "high",
            "effort": "medium",
            "rationale": "Direct impact on performance"
        },
        {
            "id": 3,
            "title": "Add query caching for 80% of reads",
            "priority": "medium",
            "effort": "medium",
            "rationale": "Long-term improvement"
        }
    ],
    "risks": [
        {
            "risk": "Optimization causes data consistency issues",
            "impact": "high",
            "mitigation": "Implement cache validation and monitoring for consistency checks"
        },
        {
            "risk": "Changes impact other services",
            "impact": "medium",
            "mitigation": "Run integration tests before and after changes"
        }
    ],
    "assumptions": [
        "Root cause is query related",
        "Database can handle optimization",
        "No breaking changes needed"
    ],
    "nextActions": [
        "Performance analysis (1-2 days)",
        "Query optimization (2-3 days)",
        "Testing and verification"
    ]
}

def load_demo_scenario(scenario_num: int):
    if scenario_num == 1:
        return DEMO_INPUT_1, DEMO_CONTEXT_1, EXPECTED_PLAN_1
    elif scenario_num == 2:
        return DEMO_INPUT_2, DEMO_CONTEXT_2, EXPECTED_PLAN_2
    elif scenario_num == 3:
        return DEMO_INPUT_3, DEMO_CONTEXT_3, EXPECTED_PLAN_3
    else:
        raise ValueError(f"Unknown scenario {scenario_num}")
