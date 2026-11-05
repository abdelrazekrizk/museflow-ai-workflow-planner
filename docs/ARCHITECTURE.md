# Architecture

## High-Level System Design

```text
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                             │
│  (argparse: --input, --input-file, --team-size, --budget, etc)  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Planner Engine                              │
│              (Orchestrates workflow + retry logic)               │
│  Input Validation → Prompt Construction → API Call → Validation │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ InputHandler │  │PromptConstructor│ │ PlanValidator│
    │ (normalize & │  │  (construct  │  │  (validate  │
    │  validate)   │  │  rich prompts)  │   schema &  │
    └──────────────┘  └──────────────┘  │  correctness)
                            │             └──────────────┘
                            │
                            ▼
                ┌────────────────────────────┐
                │  Muse Spark Integration    │
                │  (Meta Model API client)   │
                │  - API call handling       │
                │  - Timeout management      │
                │  - Error recovery          │
                └────────────────────────────┘
                            │
                            ▼
                ┌────────────────────────────┐
                │  Meta Model API (Remote)   │
                │  Muse Spark 1.3 Inference  │
                │  (reasoning + JSON output) │
                └────────────────────────────┘
```

## Data Flow

```text
1. User Input
   ├─ Brief text (50–2000 chars)
   └─ Optional context (team_size, budget, constraints, architecture_notes)
                │
                ▼
2. Input Normalization & Validation
   ├─ Trim whitespace
   ├─ Validate char counts
   └─ Preserve structure (bullets, line breaks)
                │
                ▼
3. Prompt Construction
   ├─ Inject normalized brief
   ├─ Inject optional context
   ├─ Add JSON schema spec
   ├─ Add demo example output
   └─ Add retry feedback (if retry_count > 0)
                │
                ▼
4. Meta Model API Call
   ├─ Send prompt to Muse Spark 1.3
   ├─ API client timeout: 25 seconds (planner target is 15 seconds)
   └─ Extract model text and usage metrics; JSON is parsed in validation
                │
                ▼
5. Response Parsing
   ├─ Parse JSON string
   ├─ Extract all required fields
   └─ Type-check each field
                │
                ▼
6. Plan Validation
   ├─ Schema validation (all fields present & correct type)
   ├─ Task field and limited generic-title checks (metrics are not enforced)
   ├─ Risk structure check (non-empty mitigation accepted)
   ├─ Priority presence check (distribution currently relaxed)
   └─ Alignment to input (plan addresses core challenge)
                │
       ┌────────┴────────┐
       │                 │
       ▼ (VALID)         ▼ (INVALID)
   Return Plan       Retry Logic
   with JSON         (if retries remain)
                          │
                 ┌────────┴────────┐
                 │                 │
                 ▼ (after retry budget) ▼ (retries available)
            Return Error        Refine prompt
            + Partial Plan      + Retry counter
                                + Failure type
                                     │
                                     └─ Back to step 3
                                        (re-call API)
```

### Technology Stack

| Component | Technology | Rationale |
| ----------- | ----------- | ----------- |
| **Language** | Python 3.14+ | Widely available; strong API integrations |
| **API Client** | OpenAI SDK (`openai>=3.45.0`) | OpenAI-compatible client for Meta Model API |
| **CLI Framework** | `argparse` (standard library) | No external dependency; sufficient for MVP |
| **JSON Parsing** | `json` (standard library) | Built-in; no validation needed for MVP |
| **Schema Validation** | Manual dictionary-based validation | Checks required fields and basic value types |
| **Logging** | `logging` (standard library) | Built-in; sufficient for performance metrics and error tracking |
| **Testing** | `pytest`, `pytest-mock` | Standard Python test framework; mockable API calls |

---
