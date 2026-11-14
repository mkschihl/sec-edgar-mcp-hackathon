# SEC EDGAR Project — Session Handoff (2026-11-14)

This file is the context hand-off for the next session. Read this first, then
read the files listed under "Files to load" before doing any work.

---

## Project in one sentence

An 8-tool FastMCP server (`sec_edgar_tools`) deployed to IBM Code Engine that
lets an IBM watsonx Orchestrate agent (`sec_edgar_agent`) answer questions about
SEC filings and XBRL financial data for any publicly traded company.

---

## Environment facts

| Item | Value |
|---|---|
| Workspace | `/home/itzuser/wxo-agentic-workflow/` |
| Venv | `./venv/` — Python 3.12, ADK v2.19.0, FastMCP 4.1.3 |
| WXO environment | `gsa-hackathon` — IBM Cloud Toronto (`ca-tor`) |
| WXO token lifetime | ~1 hour — refresh with `venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |
| Code Engine project | `ce-550000w6t0` — resource group `eid-6ac40a21a8799c11a48dc107` |
| CE app URL | `https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp` |
| IBM Cloud login | `ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default` then `ibmcloud target -g eid-6ac40a21a8799c11a48dc107` then `ibmcloud ce project select --name ce-550000w6t0` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` — branch `main` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1 — 8-tool MCP server | ✅ Complete | Deployed to Code Engine, always warm |
| M2 — Toolkit re-imported as remote HTTP | ✅ Complete | `sec_edgar_tools` using streamable_http in WXO |
| M3 — Evaluation harness | ✅ Code complete | Phoenix harness built; REST eval run shows 20/20; blocked on USAI for LLM-as-judge run |

---

## What was completed in the last two sessions (2026-11-11 → 2026-11-14)

### Phoenix eval harness (`eval/phoenix/`)
Full Arize Phoenix LLM-as-judge harness built and committed. Connects directly
to the Code Engine `/mcp` endpoint over streamable-HTTP (no subprocess). Two
LLM-as-judge evaluators: `match_expected_response` (correctness) and
`check_answer_scope` (scope compliance). 20-question dataset CSV covers all
8 tools. Two system prompt versions for A/B comparison.
**Blocked on:** `USAI_API_KEY` and `USAI_BASE_URL` in `.env` — these come from
the GSA hackathon lab portal (OpenAI-compatible LiteLLM gateway), NOT from the
WXO instance.

### Human quality audit (`evaluation/response_quality_audit.md`)
Full human review of all 20 agent responses from the 2026-11-07 eval run.
Key findings: YTD values returned as quarterly figures (BQ-09/10/20), wrong
entity selected for ExxonMobil (BQ-18), two annual fact inaccuracies (BQ-07).

### Server fix (`toolkits/sec_edgar_tools/server.py`)
`sec_edgar_get_quarterly_facts` now filters to genuine 3-month periods by
comparing `start`/`end` date duration (≤104 days). Deduplication per `(fp, fy)`
pair added. Q4 limitation (no 10-Q filed for fiscal Q4) surfaced in notes.
**Verified live:** Apple Q3 FY2026 revenue now $109.4B (was $364.4B YTD).

### Agent instruction update (`agents/sec_edgar_agent.yaml`)
5 instruction improvements derived from the human audit:
1. Entity disambiguation — prefer operating entity over holding shell; retry
   if no 10-K found
2. Full `resolve_company` output — always include CIK, ticker, SIC, state
3. Empty filings warning — flag when entity has no filings of requested type
4. Concept synonyms — revenue/debt concepts use non-obvious tag names; run
   synonym searches
5. Q4 limitation disclosure — explicitly explain Q4 is not in 10-Qs
**Deployed:** `orchestrate agents import` confirmed `sec_edgar_agent` updated.

### Interpretation narrative (`evaluation/interpretation.md`)
Full evaluation report covering: 3-layer measurement framework, tool utilisation
table with interpretation, 5 labelled response quality issues with root causes,
gap analysis (what automated scoring missed), and next steps.

---

## The one remaining task (once USAI credentials arrive)

```bash
# 1. Fill in .env at repo root
USAI_API_KEY=<from GSA hackathon lab portal — NOT your WXO API key>
USAI_BASE_URL=<gateway URL from lab portal — appends /api/v1 automatically>

# 2. Install eval deps (already done, but verify)
venv/bin/python -m pip install -r requirements-eval.txt

# 3. Start Phoenix server
venv/bin/python -m phoenix.server.main serve &
# UI at http://localhost:6006, OTLP at :4317

# 4. Upload dataset (one-time)
cd eval/phoenix
python create_dataset.py --dataset-name sec-edgar-eval-0

# 5. Run experiments
python run_experiment.py --dataset-name sec-edgar-eval-0
python run_experiment.py --dataset-name sec-edgar-eval-0 --system-prompt-version v2

# 6. Open Phoenix UI to review per-question scores and traces
# http://localhost:6006
```

---

## What to work on while waiting for USAI credentials

The formal milestones (M1, M2, M3) are all either done or waiting on USAI.
The following are high-value additions that extend the project beyond the
milestone scope — all are doable now with no external credentials.

### Option A — Demo walkthrough document ⭐ (recommended first)
Write `docs/demo_walkthrough.md`: a scripted 6–8 question sequence that
showcases all 8 tools in a logical progression. This is your hackathon
submission demo script. No credentials needed — agent is live in WXO UI.
Suggested flow:
  1. Search by name (search_companies)
  2. Resolve by ticker (resolve_company)
  3. List recent 10-K filings (get_recent_filings)
  4. Annual net income history (get_company_fact)
  5. Quarterly revenue trend (get_quarterly_facts)
  6. Discover available concepts (list_concepts)
  7. Cross-company comparison with warnings (compare_companies)
  8. Source filing attribution with EDGAR link (get_filing_metadata)

### Option B — Fix BQ-07 annual fact accuracy (server.py)
The `get_company_fact` tool returns all XBRL observations for a concept,
including comparative-period restated entries. FY2024 Apple net income was
off by $3B. Fix: for FY-labelled observations, keep only the one with the
latest `filed` date per fiscal year end date. This is a 10-line server.py
change, same deploy pattern as the quarterly fix.

### Option C — Hackathon submission write-up
Write `docs/submission.md` tying everything together: problem statement,
architecture diagram (Mermaid), tool descriptions, eval results summary,
and what the Phoenix experiment will add. Most content already exists across
`evaluation/interpretation.md`, `TEST_REPORT.md`, and the agent YAML.

### Option D — Expand the demo agent prompt starter list
Add 2–3 more starter prompts to `agents/sec_edgar_agent.yaml` covering
quarterly facts and concept discovery (currently underrepresented in the
starters). Deploy with `orchestrate agents import`.

---

## Key files to load at the start of the next session

```
agents/sec_edgar_agent.yaml           ← current agent instructions
toolkits/sec_edgar_tools/server.py    ← current server (8 tools)
evaluation/EVAL_REPORT.md             ← 20-question eval results (2026-11-07)
evaluation/response_quality_audit.md  ← human annotations of all 20 responses
evaluation/interpretation.md          ← narrative evaluation report
eval/phoenix/README.md                ← Phoenix harness usage guide
.env.example                          ← documents all required env vars
```

---

## Git log (last 5 commits)

```
84cd8e2  fix+docs(eval): human audit findings → server fix, instruction update, interpretation
45d01fe  feat(eval): add Phoenix LLM-as-judge evaluation harness (M3)
22b96d9  chore(.bob/skills): update skill set for Code Engine deploy session
de7e149  feat: add Code Engine HTTP deployment for sec_edgar_tools
6560ccb  fix(sec_edgar_tools): set trust_env=False and follow_redirects=True on shared httpx client
```

---

## Skills to activate

- `wxo-builder` — full ADK/orchestrate CLI reference
- `mcp-eval` — Phoenix eval harness patterns (if continuing eval work)
