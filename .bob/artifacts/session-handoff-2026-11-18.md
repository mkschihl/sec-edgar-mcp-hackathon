# SEC EDGAR Project — Session Handoff (2026-11-18, end of session)

Read this file first, then the files listed under "Key files" before doing any work.

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
| Venv | `./venv/` — Python 3.12 |
| arize-phoenix-evals | 3.9.5 |
| arize-phoenix-client | 3.7.0 |
| WXO environment | `gsa-hackathon` — IBM Cloud Toronto (`ca-tor`) |
| WXO token refresh | `source .env && export WXO_API_KEY && venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |
| Re-import agent | `venv/bin/orchestrate agents import -f agents/sec_edgar_agent.yaml` |
| Code Engine project | `ce-550000w6t0` — resource group `eid-6ac40a21a8799c11a48dc107` |
| CE app URL | `https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp` |
| CE login | `ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default` then `ibmcloud target -g eid-6ac40a21a8799c11a48dc107` then `ibmcloud ce project select --name ce-550000w6t0` |
| CE deploy command | `ibmcloud ce app update --name sec-edgar-tools-mks --build-source toolkits/sec_edgar_tools --build-dockerfile Dockerfile` |
| watsonx.ai URL | `https://ca-tor.ml.cloud.ibm.com` |
| watsonx.ai project ID | `2d244f0a-a04f-4585-b4eb-94da0b59541a` |
| Phoenix server | Already running on this VM — UI at http://localhost:6006 — check: `ss -tlnp \| grep 6006` |
| Phoenix run command | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL && venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml` |
| Run evaluator (no Phoenix) | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID JUDGE_MODEL && venv/bin/python eval/phoenix/score_wxo_results.py` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` |
| Active branch | `fixes-round2` |
| Last commit | `2966d5e` — "docs: update interpretation.md and submission.md with correct scores; pin requirements.txt" |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |
| Active model vars | `AGENT_MODEL=meta-llama/llama-3-3-70b-instruct` / `JUDGE_MODEL=mistralai/mistral-small-3-1-24b-instruct-2503` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1 — 8-tool MCP server | ✅ Complete | Deployed to Code Engine, always warm |
| M2 — Toolkit re-imported as remote HTTP | ✅ Complete | `sec_edgar_tools` using streamable_http in WXO |
| M3 — Evaluation harness | ✅ Complete | Phoenix eval-0 (20 Qs), human audit, Phoenix eval-2 (23 Qs) all done |
| M4 — Eval code improvements | ✅ Complete | 23 Qs, numeric judge, routing, filing_index_url, majority vote |
| M5 — Judge quality & stability | ✅ Complete | Majority vote, 11/11 sanity pass, BQ-10h fixture |
| M6 — Q4 derivation + BQ-15/16/09/10 | ✅ Complete | Server derives Q4; all numeric anchors pass; docs updated |
| **M7 — docs/submission.md final scores** | ✅ **Complete** | 21/23 correct, 2 unstable, 23/23 scope, 8/8 numeric |
| **M8 — Merge fixes-round2 → main** | ⏳ **TODO** | All work done; ready to merge |

---

## This session's changes (commits `a57eebf` → `2966d5e`)

### `a57eebf` — Q4 derivation, Rule 6/8 agent update, BQ-15/16 numeric_checks

**`toolkits/sec_edgar_tools/server.py`:**
- `sec_edgar_get_quarterly_facts`: derives Q4 for USD flow concepts as
  `annual FY (10-K, 350–380 days) − nine-month YTD (fp=Q3, 260–285 days, same period_start)`.
  Derived rows: `derived: true`, `derivation: "annual (<accn>) minus nine-month YTD (<accn>)"`.
  Per-share units, share counts, and instant (balance-sheet) facts skipped with note.
  Real Q1–Q3 rows: `derived: false`.
- `from datetime import timedelta` added to module imports.

**`evaluation/benchmark_questions.py`:**
- BQ-15 `numeric_checks`: `must_include [478.834e9]`, `rel_tol 0.005` (AAPL revenue FY2026-09-26)
- BQ-16 `numeric_checks`: `must_include [133.749e9]`, `rel_tol 0.005` (MSFT NetIncomeLoss FY2026-06-30)
- Both `pass_criteria` updated to state the specific value.

**`agents/sec_edgar_agent.yaml`:**
- Rule 6: new FIRST bullet — "Your answer MUST state the value itself (e.g. 'Revenue: $478.8 billion, fiscal year ended 2026-09-26') before the filing details. An answer that names a filing without the number is incomplete." Old duplicate "state the value" bullet removed.
- Rule 8: Q4 LIMITATION bullet replaced — "Q4 values marked derived: true are computed as annual minus nine-month YTD. Label them '(derived)' and include the derivation note. If Q4 is absent (e.g. EPS), explain that it cannot be derived because per-share values are not additive."

**`toolkits/sec_edgar_tools/test_regressions.py`:** 3 new tests (13, 14, 15):
- [13] MSFT NetIncomeLoss Q4 derived: Q4 FY2026 ending 2026-06-30, `derived=True`, value=35,766,000,000; 6 distinct period_ends
- [14] AAPL Revenues FY2025 Q1+Q2+Q3+Q4 == 416,161,000,000 (exact, within $1M)
- [15] AAPL EPS: no derived rows; note explains per-share unit not additive
- All 80+ assertions pass.

**`eval/phoenix/datasets/sec-edgar-eval-2.csv`**: rebuilt (8 Qs with numeric_checks, was 6).

### `571f523` — BQ-09/10 derived-Q4 pass_criteria; BQ-10 must_include 35.766e9; BQ-10h sanity fixture

**`evaluation/benchmark_questions.py`:**
- BQ-09 `pass_criteria`: added sentence — "Fiscal Q4 rows marked '(derived)' are computed as annual minus nine-month YTD; they are legitimate single-quarter values, not year-to-date totals, and are correct."
- BQ-10 `pass_criteria`: same sentence + "Q4 FY2026 (ended 2026-06-30) ≈ $35.8B (derived: annual minus nine-month YTD)."
- BQ-10 `must_include`: added `35.766e9` → now `[36.629e9, 31.778e9, 38.458e9, 35.766e9]`.

**`eval/phoenix/judges/fixtures/BQ-10h.txt`**: current BQ-10 agent response (includes Q4 FY2026 derived row, $35.77B).

**`eval/phoenix/judges/sanity_check.py`:**
- New case BQ-10h: `expect_correctness=correct`, `expect_scope=within_scope`, `expect_numeric=(==, 1.0)`.
- BQ-10f updated: scope-only test (no `expect_correctness`; old fixture predates Q4); `expect_numeric=(<, 1.0)`.
- `main()`: correctness judge block guarded with `if "expect_correctness" in case`.
- Sanity result: **11/11 PASS**.

**`score_wxo_results.py` on `raw_results.json` (commit 571f523):**
```
correctness=21/23  (2 unstable: BQ-18, BQ-22)  scope=23/23  numeric=8/8
```

### `2966d5e` — docs update + requirements.txt pin

**`toolkits/sec_edgar_tools/requirements.txt`**: pinned `fastmcp==4.1.3`, `httpx==0.28.1`, `pydantic==2.14.3`.

**`evaluation/interpretation.md`**: fully updated —
- Layer 1 caveat: routing counts from text matching (not live WXO events)
- Layer 3 description: Llama-agent Phoenix runs (via Code Engine MCP) vs. production WXO scoring
- Issues 3–7: all marked fixed (Q4 derivation, annual dedup, revenue candidates, URL prohibition)
- Section 6: Llama-agent (17–18/20) and production WXO (21/23 correct + 2 unstable, 23/23 scope, 8/8 numeric; Mistral Small 3-vote majority; run 2026-11-18, commit 571f523)
- "Zero hallucination" language removed; replaced with structural fabrication-guard description

**`docs/submission.md`**: fully updated — same corrections plus:
- Problem statement: "zero hallucination risk" → structural tool-call mandate description
- Tool 5: Q4 derivation described
- Layer 3: Llama-agent vs. production WXO correctly separated
- Key Technical Decisions: Q4 derivation, revenue concept selection, 3-vote majority judge added
- Phoenix summary: both signal types with correct numbers

---

## Current evaluation state

### `score_wxo_results.py` on `raw_results.json` (run 2026-11-18, commit `571f523`):

```
correctness=21/23  (2 unstable)  scope=23/23  numeric=8/8 (of 8 with checks)
```

Unstable questions (2-of-3 vote split):
- **BQ-18** — Exxon search → 10-K filings (one judge vote flags filing period-end dates as post-today)
- **BQ-22** — Tesla investment advice refusal (judge uncertain whether refusal was complete enough)

Incorrect questions: **none** — all 21 non-unstable are unanimously `correct`.

### Sanity check: **11/11 PASS** (run 2026-11-18)

Cases: BQ-07a, BQ-07b, BQ-09c, BQ-09d, BQ-09e, BQ-07f, BQ-10f (scope only), BQ-10h, BQ-17d, BQ-17g, BQ-17e.

### Phoenix datasets:
- `sec-edgar-eval-1`: id `RGF0YXNldDoy`, 23 examples — OLD schema (do not re-use)
- `sec-edgar-eval-2`: id `RGF0YXNldDoz`, 23 examples — CURRENT, correct schema
  - CSV was rebuilt in `571f523` (8 Qs with numeric_checks)
  - **Needs re-upload** before next Phoenix experiment: `venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2`
- Last Phoenix experiment on eval-2 (pre-majority-vote): `RXhwZXJpbWVudDo4` — correctness=14/23, scope=19/23, numeric=3/5 (stale — many fixes since)

### Agent import status:
- Agent was re-imported in commit `5ebd3cc` with Rule 6 fix.
- **Rule 6 first bullet** (value-first mandate) and **Rule 8** (Q4 derived rows) were updated in `a57eebf` but the agent has **NOT been re-imported** since then. Re-import is needed before the next Phoenix run.

---

## Discoveries (critical for new sessions)

### WXO token refresh pattern (MUST use `--api-key` flag)
`orchestrate env activate gsa-hackathon` without `--api-key` reads from stdin — in a non-interactive session it gets empty string → IBM IAM 400. Always use:
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
```

### Majority-vote judge (`correctness_judge.py`)
- `majority_vote_correctness(q, r, ref)` → 3 runs → majority label
- Returns: `label`, `score`, `explanation`, `all_explanations: list[str]`, `stable: bool`
- `unstable` = 2-of-3 split → `score=0.5`
- `match_expected_response()` (Phoenix) strips `all_explanations`/`stable` — Phoenix only accepts `label/score/explanation`
- `score_wxo_results.py` prints all 3 explanations for unstable/incorrect

### Phoenix experiment API (arize-phoenix-client 3.7.0)
- `Client(base_url=phoenix_endpoint)` — not `Client(endpoint=...)`
- Numeric judge metadata unpacking: Phoenix passes `{"metadata": "<json-str>"}` envelope — must do `json.loads(metadata["metadata"])` to get `numeric_checks`
- `c.datasets.list()` returns `list[dict]`; `c.experiments.list(dataset_id=...)` returns experiment dicts
- GraphQL endpoint at `/graphql`; use `node(id: "...")` with `... on Experiment { runs { ... } }` to fetch runs + annotations

### Judge training-cutoff contamination (mostly fixed)
- Mistral-Small-3.1 originally flagged 2025–2026 SEC data as "future forecasts"
- Fixed by: (a) today's date sentence, (b) fiscal-year clarification paragraph — `"A period whose end date is on or before {today} is historical..."`
- Residual: BQ-08 scope (Amazon FY2026 ends Dec 31 2026 — genuinely in the future for the judge if run before that date)

### Q4 derivation (server-side, `sec_edgar_get_quarterly_facts`)
- Finds annual FY (fp=FY, 10-K, 350–380 days) and nine-month YTD (fp=Q3, 260–285 days) sharing same `period_start`
- Q4 = annual − nine-month YTD; period: start = day after nine-month end, end = annual end
- Only for `best_unit == "USD"` and flow items (obs have `start` date)
- Skipped (with note) for: `USD/shares`, `shares`, or instant facts (no `start`)
- Derived rows: `fiscal_quarter="Q4"`, `derived=True`, `derivation="annual (<accn>) minus nine-month YTD (<accn>)"`
- Real rows: `derived=False`

### `sec_edgar_get_company_fact` row fields
Every row now includes: `filing_index_url` (deterministic EDGAR archive URL), `form`, `filed`, `accession_number`. This is why BQ-15/16 can use `get_company_fact` alone (without `get_filing_metadata`) for form/date questions.

### `filing_index_url` formula (server-side, no extra HTTP call)
`https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number.replace('-','')}/"` — deterministic from accession number already in fact data.

---

## Key files

```
agents/sec_edgar_agent.yaml              ← UPDATED (a57eebf): Rule 6 value-first mandate;
                                           Rule 8 Q4 derived rows; NOT yet re-imported to WXO

toolkits/sec_edgar_tools/server.py       ← UPDATED (a57eebf): Q4 derivation in
                                           sec_edgar_get_quarterly_facts; derived/derivation fields;
                                           filing_index_url in fact rows; REVENUE_CANDIDATES
toolkits/sec_edgar_tools/requirements.txt ← PINNED (2966d5e): fastmcp==4.1.3, httpx==0.28.1, pydantic==2.14.3
toolkits/sec_edgar_tools/test_regressions.py ← 80+ assertions (tests 13/14/15 added); all pass

eval/phoenix/run_experiment.py           ← unchanged; use --dataset-name sec-edgar-eval-2
                                           --system-prompt-version yaml
eval/phoenix/agent.py                    ← unchanged
eval/phoenix/build_dataset.py            ← builds CSV; default=sec-edgar-eval-2
eval/phoenix/create_dataset.py           ← uploads to Phoenix; run after rebuild
eval/phoenix/score_wxo_results.py        ← majority vote; unstable reporting; all 3 explanations on fail
eval/phoenix/datasets.yaml               ← sec-edgar-eval-2 entry
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← CURRENT (rebuilt 571f523, 8 Qs with numeric_checks)

eval/phoenix/judges/__init__.py          ← exports majority_vote_correctness
eval/phoenix/judges/correctness_judge.py ← _single_classify, _majority_vote,
                                           majority_vote_correctness, match_expected_response (3-run)
eval/phoenix/judges/relevance_judge.py   ← 3-attempt retry, judge_error return
eval/phoenix/judges/numeric_judge.py     ← deterministic: {must_include, rel_tol, max_value}
eval/phoenix/judges/sanity_check.py      ← UPDATED (571f523): 11 cases; BQ-10h; expect_correctness
                                           guard; 11/11 PASS (last run)
eval/phoenix/judges/fixtures/
  BQ-07f.txt    ← Apple net income FY2022–FY2026 (scope fix validation)
  BQ-09e.txt    ← Apple quarterly revenue 8 quarters (actual WXO response)
  BQ-10f.txt    ← MSFT quarterly net income without Q4 (scope-only test)
  BQ-10h.txt    ← MSFT quarterly net income WITH Q4 FY2026 derived row (CURRENT correct response)
  BQ-17d.txt    ← Pfizer wrong-concept response (expect incorrect)
  BQ-17g.txt    ← Pfizer CURRENT correct response (expect correct)

evaluation/run_evaluation.py             ← --ids merges into raw_results.json by id
evaluation/benchmark_questions.py        ← UPDATED (571f523): BQ-09/10 derived-Q4 pass_criteria;
                                           BQ-10 must_include [36.629e9, 31.778e9, 38.458e9, 35.766e9];
                                           BQ-15 must_include [478.834e9]; BQ-16 must_include [133.749e9]
evaluation/raw_results.json              ← 23 results (all BQ-01→BQ-23)
evaluation/traces/                       ← BQ-01 through BQ-23 trace JSON files

docs/submission.md                       ← UPDATED (2966d5e): 21/23 correct, 2 unstable,
                                           23/23 scope, 8/8 numeric; Llama-agent vs production
                                           WXO clearly separated; fabrication guard described
evaluation/interpretation.md             ← UPDATED (2966d5e): same corrections; Layer 1 text-match
                                           caveat; Issues 3–7 all marked fixed
```

---

## Git log (last 10 commits)

```
2966d5e  docs: update interpretation.md and submission.md with correct scores; pin requirements.txt
571f523  fix(eval): BQ-09/10 derived-Q4 pass_criteria; BQ-10 must_include 35.766e9; BQ-10h sanity fixture
a57eebf  feat(server): Q4 derivation (annual minus nine-month YTD); Rule 6/8 agent update; BQ-15/16 numeric_checks
7ccbdb3  fix(eval): BQ-17 FY2023 mislabel guard, BQ-10 numeric_checks, BQ-07 period-end dates
5ebd3cc  fix(agent): Rule 6 — mandate get_company_fact before get_filing_metadata for BQ-15
5aeddb0  fix(eval): majority-vote correctness judge (3-run), BQ-17g fixture, Rule 6 value mandate
5f33af1  fix(eval): BQ-14 numeric values, fiscal-year date context, routing_ok/diff, sanity f cases
d3132a4  fix(eval): judge date context, numeric no-op, sec-edgar-eval-2 dataset, agent OOS rule
ed4977b  fix(eval): remove duplicate import in run_evaluation.py; BQ-16 optional_tools
b6085ed  fix(eval): judge retry, BQ-17 alignment, filing_index_url, fixture files
```

---

## Next steps (recommended order)

### 1. Re-import agent to WXO
Rules 6 and 8 were updated in `a57eebf` but **not yet re-imported**:
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
venv/bin/orchestrate agents import -f agents/sec_edgar_agent.yaml
```

### 2. Re-upload sec-edgar-eval-2 dataset to Phoenix
CSV was rebuilt in `571f523` (8 Qs with numeric_checks):
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID
venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2
```

### 3. Run full Phoenix experiment on sec-edgar-eval-2
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
venv/bin/python eval/phoenix/run_experiment.py \
  --dataset-name sec-edgar-eval-2 \
  --system-prompt-version yaml
```
Expected: correctness should approach or exceed 21/23 (the score_wxo_results.py baseline).

### 4. Merge fixes-round2 → main
All work is complete. After Phoenix run:
```bash
git checkout main && git merge fixes-round2 && git push origin main
```

---

## Skills to activate

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns (`.bob/skills/mcp-eval-wxai/SKILL.md`)
