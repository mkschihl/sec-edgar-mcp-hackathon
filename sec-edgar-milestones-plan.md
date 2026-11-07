# SEC EDGAR — Milestones 2 & 3 Plan

## Context

All five sub-tasks from `sec-filing-explorer-plan.md` are complete. The toolkit
(`sec_edgar_tools`) has six tools deployed to `gsa-hackathon`. Two milestones
remain:

| Milestone | Due | What is needed |
|---|---|---|
| **M2** | 2026-10-26 | All custom tools populated for initial evaluation |
| **M3** | 2026-11-03 | Benchmark question set created; ≥1 evaluation run + interpretation |

This plan covers the work needed for both.

---

## Milestone 2 — Complete the Tool Set (2026-10-26)

Two tools are missing before the toolkit is ready for evaluation:

1. **`sec_edgar_list_concepts`** — lets the agent (and users) discover what XBRL
   concepts are actually available for a company, so they don't have to guess
   names like `Revenues` or `NetIncomeLoss`. Without this, concept lookup is
   trial-and-error.

2. **`sec_edgar_get_quarterly_facts`** — pulls Q1/Q2/Q3/Q4 observations for a
   concept so users can ask "show me quarterly revenue for the last two years"
   rather than only annual figures.

---

### Sub-Task A — Add `sec_edgar_list_concepts` to `server.py`

**Intent:** Give the agent a way to answer "what financial concepts does this
company report?" so it can route correctly without guessing XBRL tag names.

**Expected Outcomes:**
- `sec_edgar_list_concepts` is registered as a seventh `@mcp.tool`
- Given a ticker/CIK and optional taxonomy filter, it returns a flat list of
  available concept names with their human-readable labels
- If the concept list is long, it supports a `search` parameter for substring
  filtering (e.g. `search="revenue"` returns only revenue-related concepts)
- Returns an error dict with hint on failure

**Tool Specification:**
- **Name:** `sec_edgar_list_concepts`
- **Inputs:**
  - `identifier: Annotated[str, "Ticker or CIK"]`
  - `taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap'. Default 'us-gaap'."] = "us-gaap"`
  - `search: Annotated[str, "Optional substring filter on concept name or label, e.g. 'revenue'. Case-insensitive."] = ""`
  - `limit: Annotated[int, "Max concepts to return. Default 50, max 200."] = 50`
- **Implementation:** Fetch `companyfacts/CIK{padded}.json` (same endpoint as
  `sec_edgar_get_company_fact`). Navigate `facts[taxonomy]`. For each concept key,
  extract `label` and `description`. Apply case-insensitive substring filter on
  both concept name and label if `search` is provided. Sort alphabetically.
  Slice to `limit`.
- **Returns:**
```json
{
  "company": "Apple Inc.",
  "cik": "0000320193",
  "taxonomy": "us-gaap",
  "search": "revenue",
  "total_matches": 4,
  "concepts": [
    {"concept": "RevenueFromContractWithCustomerExcludingAssessedTax",
     "label": "Revenue from Contract with Customer, Excluding Assessed Tax"},
    {"concept": "Revenues", "label": "Revenues"},
    ...
  ]
}
```

**Relevant Context:**
- Pattern: every other tool in `toolkits/sec_edgar_tools/server.py` — same
  `@mcp.tool` decorator, `Annotated` params, `_ensure_ticker_cache`, error dict
- Reuses `_TICKER_CACHE` and the `companyfacts` endpoint already used by
  `sec_edgar_get_company_fact`

**Agent instruction addition:** Add rule: *"When a user asks what financial data
is available for a company, or when a concept name fails, call
`sec_edgar_list_concepts` with a relevant search term to find the correct name."*

**Status:** [x] done

---

### Sub-Task B — Add `sec_edgar_get_quarterly_facts` to `server.py`

**Intent:** Enable quarterly drill-down so the agent can answer questions like
"show me quarterly revenue for Apple over the last 8 quarters."

**Expected Outcomes:**
- `sec_edgar_get_quarterly_facts` is registered as an eighth `@mcp.tool`
- Returns only quarterly observations (fp in Q1/Q2/Q3/Q4) for a concept, most
  recent first, sliced to `limit`
- Clearly labels each observation with its quarter label (Q1 FY2025, etc.)
- Warns if quarterly data is sparse or unavailable

**Tool Specification:**
- **Name:** `sec_edgar_get_quarterly_facts`
- **Inputs:**
  - `identifier: Annotated[str, "Ticker or CIK"]`
  - `taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap'."]`
  - `concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues'."]`
  - `limit: Annotated[int, "Number of quarterly observations to return. Default 8, max 40."] = 8`
- **Implementation:**
  - Fetch `companyfacts/CIK{padded}.json` — same as `sec_edgar_get_company_fact`
  - Navigate `facts[taxonomy][concept].units`
  - Pick the dominant unit (most observations), same logic as `compare_companies`
  - Filter observations where `fp` is in `{"Q1", "Q2", "Q3", "Q4"}` AND
    `form` starts with `10-Q` (quarterly filings, not restated annual)
  - Sort by `end` date descending, slice to `limit`
  - Add a human-readable `period_label` to each observation: e.g. `"Q1 FY2025"`
    derived from `fy` and `fp` fields
  - If fewer than `limit` quarterly observations exist, emit a `note` key
    explaining how many were found
- **Returns:**
```json
{
  "company": "Apple Inc.",
  "cik": "0000320193",
  "taxonomy": "us-gaap",
  "concept": "Revenues",
  "unit": "USD",
  "label": "Revenues",
  "observations": [
    {"period_label": "Q3 FY2025", "end": "2025-06-28", "val": 85777000000,
     "form": "10-Q", "accn": "0000320193-25-000062", "fy": 2025, "fp": "Q3"},
    ...
  ],
  "note": ""
}
```

**Relevant Context:**
- Very similar internal logic to `sec_edgar_get_company_fact` — share the CIK
  resolution and cache warming pattern; differ only in the `fp` filter and
  descending sort
- Apple and most large companies do have rich quarterly XBRL data going back 10+
  years — this tool will surface it cleanly

**Agent instruction addition:** Add rule: *"When a user asks for quarterly data,
quarterly trends, or asks about specific quarters (Q1, Q2, Q3, Q4), call
`sec_edgar_get_quarterly_facts` instead of `sec_edgar_get_company_fact`."*

**Status:** [x] done

---

### Sub-Task C — Update tests, re-deploy, update agent

**Intent:** Keep `test_local.py` honest and get the two new tools live in
Orchestrate.

**Expected Outcomes:**
- `test_local.py` has checks for both new tools (discovery + at least one
  quarterly data check for AAPL `Revenues`)
- `./scripts/import-all.sh` re-imports the updated toolkit (Orchestrate
  replaces the existing `sec_edgar_tools` toolkit in-place) and the updated
  agent YAML
- `orchestrate tools list` shows all eight `sec_edgar_*` tools
- The agent instructions reference both new tools

**Todo List:**
1. Add tests for `sec_edgar_list_concepts` and `sec_edgar_get_quarterly_facts`
   to `test_local.py` — run locally first to confirm both pass
2. Run `./scripts/import-all.sh` to re-deploy
3. Confirm 8 tools registered with `orchestrate tools list | grep sec_edgar`
4. Quick smoke-test: ask agent "What revenue concepts are available for Apple?"
   → should call `sec_edgar_list_concepts`

**Status:** [x] done

---

## Milestone 3 — Evaluation (2026-11-03)

### Sub-Task D — Design benchmark question set

**Intent:** Define a set of questions that covers every tool and every
interaction pattern, so the evaluation is both complete and interpretable.
The questions become the input to the evaluation script.

**Expected Outcomes:**
- A file `evaluation/benchmark_questions.py` containing a structured list of
  benchmark questions as Python data (list of dicts)
- Questions cover all eight tools, multiple difficulty levels, and the four
  scenario types from the original brief
- Each question has: `id`, `question` (natural language), `expected_tools`
  (list of tool names the agent should call), `category`, `difficulty`

**Benchmark Question Design:**

The questions should test these eight scenarios (one or more questions each):

| # | Scenario | Tools exercised | Difficulty |
|---|---|---|---|
| 1 | Company lookup by name (doesn't know ticker) | `search_companies` → `resolve_company` | easy |
| 2 | Company lookup by ticker | `resolve_company` | easy |
| 3 | List recent 10-K filings | `get_recent_filings` | easy |
| 4 | List recent 10-Q filings | `get_recent_filings` | easy |
| 5 | Annual financial fact — single company | `resolve_company` + `get_company_fact` | medium |
| 6 | Quarterly financial fact — single company | `resolve_company` + `get_quarterly_facts` | medium |
| 7 | Discover available concepts | `list_concepts` | medium |
| 8 | Cross-company comparison + warnings surfaced | `compare_companies` | hard |
| 9 | Source filing attribution ("which filing?") | `get_company_fact` + `get_filing_metadata` | hard |
| 10 | Multi-step: unknown company → facts → source | `search_companies` + `get_company_fact` + `get_filing_metadata` | hard |

Aim for **20 benchmark questions** total across the ten scenarios — roughly two
per scenario, varying company and concept.

**File structure (`evaluation/benchmark_questions.py`):**
```python
BENCHMARK_QUESTIONS = [
    {
        "id": "BQ-01",
        "category": "company_lookup",
        "difficulty": "easy",
        "question": "Find companies with 'Berkshire' in their name.",
        "expected_tools": ["sec_edgar_search_companies"],
        "pass_criteria": "Response lists BRK.A and/or BRK.B",
    },
    ...
]
```

**Status:** [x] done

---

### Sub-Task E — Build evaluation script and run it

**Intent:** Write a Python script that sends each benchmark question to the
deployed agent, captures the response and reasoning trace, scores each
question, and auto-generates a Markdown report.

**Expected Outcomes:**
- `evaluation/run_evaluation.py` — runnable script that:
  1. Iterates over `BENCHMARK_QUESTIONS`
  2. Calls the agent via the Orchestrate runtime REST API (not the CLI, to
     avoid the EOF quirk) using the same pattern as `chat_with_agent`
  3. Captures `response_text` and `reasoning_trace` (tool calls fired)
  4. Scores each question: **pass** / **partial** / **fail** based on:
     - Were all `expected_tools` called? (from reasoning trace)
     - Does the response contain an error key or "I don't know"?
  5. Writes `evaluation/EVAL_REPORT.md` with:
     - Summary table (pass/partial/fail counts, % pass rate)
     - Per-question rows: ID | Question | Expected Tools | Tools Fired | Score | Notes
     - Interpretation section: which tools performed well, which failed, patterns
     - Recommendations section: what to fix

- Script uses the ADK MCP `chat_with_agent` tool via Python subprocess (same
  mechanism as `orchestrate chat ask`) rather than requiring a raw REST client,
  keeping setup simple

- Script is idempotent: re-running overwrites `EVAL_REPORT.md`

**Implementation notes:**
- Use `orchestrate chat ask -n sec_edgar_agent "<question>" -r` per question
  via `subprocess.run` and parse stdout for the response and tool firings
- The `-r` flag includes reasoning trace — parse it to extract which tools
  were called
- A 2-second pause between questions respects the platform's rate limits
- Target runtime: under 5 minutes for 20 questions

**Relevant Context:**
- Pattern: `toolkits/sec_edgar_tools/test_local.py` — sequential async calls
  with assertions
- The `orchestrate chat ask` EOF quirk: response appears above the EOF flood;
  parse up to the first `EOF when reading a line` line
- Active env: `gsa-hackathon` — confirm token is live before running

**Status:** [x] done

---

## Implementation Order

```
Sub-Task A  →  Sub-Task B  →  Sub-Task C (deploy)
                                    ↓
                              Sub-Task D (questions)
                                    ↓
                              Sub-Task E (run eval)
```

A and B can be written in the same session (both edit `server.py`). C deploys
both at once. D and E are written together then executed.

## File Layout After Completion

```
toolkits/sec_edgar_tools/
├── server.py          ← 8 tools (+ list_concepts, + get_quarterly_facts)
├── requirements.txt
├── toolkit.yaml
└── test_local.py      ← updated for 8 tools

agents/
└── sec_edgar_agent.yaml ← updated instructions for 8 tools

evaluation/
├── benchmark_questions.py  ← 20 structured benchmark questions
├── run_evaluation.py       ← evaluation runner script
└── EVAL_REPORT.md          ← auto-generated results report

scripts/
├── import-all.sh
└── delete-all.sh
```
