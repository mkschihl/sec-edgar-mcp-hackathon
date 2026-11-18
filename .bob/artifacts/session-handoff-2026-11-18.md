# SEC EDGAR Project — Session Handoff (2026-11-18, end of day)

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
| Last commit | `7ccbdb3` — "fix(eval): BQ-17 FY2023 mislabel guard, BQ-10 numeric_checks, BQ-07 period-end dates" |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |
| Active model vars | `AGENT_MODEL=meta-llama/llama-3-3-70b-instruct` / `JUDGE_MODEL=mistralai/mistral-small-3-1-24b-instruct-2503` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1 — 8-tool MCP server | ✅ Complete | Deployed to Code Engine, always warm |
| M2 — Toolkit re-imported as remote HTTP | ✅ Complete | `sec_edgar_tools` using streamable_http in WXO |
| M3 — Evaluation harness | ✅ Complete | Phoenix run complete — eval-0 (20 Qs) done previously |
| M4 — Eval code improvements | ✅ Complete | 23 Qs, numeric judge, routing, filing_index_url |
| M5 — Judge quality & stability | ✅ Complete (this session) | Majority vote, correct references, 10/10 sanity pass |
| **M6 — Full Phoenix re-run on eval-2** | ⏳ **TODO** | Re-run after agent re-import with updated YAML |
| **M7 — docs/submission.md final scores** | ⏳ **TODO** | Fill in scores from M6 run |
| **M8 — Merge fixes-round2 → main** | ⏳ **TODO** | After M7 |

---

## This session's changes (commits `5aeddb0` → `7ccbdb3`)

### `5aeddb0` — majority-vote correctness judge + BQ-17g fixture + Rule 6 value mandate

**`eval/phoenix/judges/correctness_judge.py`:**
- `_single_classify()`: runs classifier once with 3-attempt retry (extracted from previous inline loop)
- `_majority_vote(runs)`: aggregates 3 runs → `correct`/`incorrect` (unanimous, `stable=True`) or `unstable` (2-of-3, `stable=False`, `score=0.5`); always returns `all_explanations: list[str]`
- `majority_vote_correctness(question, response, reference)`: new public function — builds classifier, runs 3×, returns full dict
- `match_expected_response()` (Phoenix evaluator): uses same 3-run majority; strips `all_explanations`/`stable` before returning to Phoenix
- `judges/__init__.py`: exports `majority_vote_correctness`

**`eval/phoenix/score_wxo_results.py`:**
- Uses `majority_vote_correctness` (3 runs per question)
- `⚠` icon for unstable, `❌` for incorrect, `✅` for correct
- Prints all 3 explanations for unstable or incorrect results
- SUMMARY line reports `(N unstable)` count

**`eval/phoenix/judges/fixtures/BQ-17g.txt`**: current BQ-17 response from `raw_results.json` (Pfizer, correct Revenues concept)

**`eval/phoenix/judges/sanity_check.py`:**
- `_run_correctness` now calls `majority_vote_correctness` directly (retains `all_explanations`)
- BQ-17g case added → `expect_correctness: correct` + `expect_numeric: (==, 1.0)`
- Prints all 3 explanations on failure

**`agents/sec_edgar_agent.yaml` Rule 6:**
- Added: `→ Always state the value itself alongside the filing details`

**`evaluation/benchmark_questions.py`:**
- BQ-17 `pass_criteria`: explicit FY2025 value, FY2022 original/recast both acceptable, FY2025 clarified as historical
- BQ-10 `pass_criteria`: added unique-period-end-date requirement + FY2027 Q1 label explanation

### `5ebd3cc` — Rule 6 mandate get_company_fact before get_filing_metadata (BQ-15 fix)

**`agents/sec_edgar_agent.yaml` Rule 6** rewritten:
- New first bullet: `→ To find which filing reported a number, you MUST first call sec_edgar_get_company_fact (or sec_edgar_compare_companies) for that metric. Take the accession_number from the most recent row, then call sec_edgar_get_filing_metadata with it. Do not use sec_edgar_get_recent_filings to answer "which filing reported X" questions; the latest 10-K is not always the source of a given value.`
- Then: `→ Present the edgar_viewer_url from sec_edgar_get_filing_metadata.`
- **Agent re-imported to WXO** (`Agent 'sec_edgar_agent' updated successfully`)

### `7ccbdb3` — BQ-17/10/07 pass_criteria + BQ-10 numeric_checks

**`evaluation/benchmark_questions.py`:**

**BQ-17** (`FY2023` mislabel guard):
- Removed `"$62.6B OR"` from FY2023 — $62.6B is the FY2025 value
- Correct FY2023: `"$59.6B (recast) or $58.5B (as originally filed)"`
- Added explicit guard: `"Do NOT accept $62.6B for FY2023 — that is the FY2025 value; reporting it for FY2023 is a year-mislabeling error."`

**BQ-10** (new `numeric_checks` from live tool call):
- Replaced `"Mark correct if each row..."` with `"Values must be single-quarter (not year-to-date) amounts."`
- Added anchor values: `Q1 FY2027=$36.629B, Q3 FY2026=$31.778B, Q2 FY2026=$38.458B`
- `numeric_checks`: `{"must_include": [36.629e9, 31.778e9, 38.458e9], "rel_tol": 0.005, "max_value": None}`

**BQ-07** (FY2025/FY2026 period-end dates explicit):
- Added: `"FY2025 ended 2025-09-27 (~$112B) and FY2026 ended 2026-09-26 (~$132B) are both historical (period ends before 2026-11-18) and correct if present."`

**`eval/phoenix/judges/sanity_check.py`:**
- BQ-10f: `expect_numeric` updated from `(any)` to `(==, 1.0)` (now that BQ-10 has checks)
- BQ-17e: response shifted further (8-12% off) to avoid borderline instability
- BQ-07f: comments updated

**`eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv`**: rebuilt (6 Qs with numeric_checks, was 5)

---

## Current evaluation state

### `score_wxo_results.py` on `raw_results.json` (23 cached results, latest run):

```
correctness=20/23  (3 unstable)  scope=23/23  numeric=5/5
```

Unstable questions (3 votes split 2-1):
- **BQ-13** — compare net income for AAPL/MSFT/GOOG (judge uncertain whether all 3 companies present)
- **BQ-15** — Apple filing attribution (judge uncertain whether revenue amount was stated alongside URL)
- **BQ-22** — Tesla investment advice refusal (judge uncertain whether refusal was complete enough)

Incorrect questions (unanimous 3-of-3 wrong):
- None in `raw_results.json` — all 20 non-unstable are `correct`

Routing notes:
- **BQ-19** (`score=fail`): agent correctly reported "ticker not found" but skipped `sec_edgar_get_recent_filings` — routing_diff. The `pass` criteria says the response is acceptable ("gracefully reports that the ticker was not found"). `score=fail` is stale from an older evaluation run; re-score will fix this.
- **BQ-15** routing now `routing_ok` after Rule 6 fix and agent re-import.

### Phoenix datasets:
- `sec-edgar-eval-1`: id `RGF0YXNldDoy`, 23 examples — OLD schema (do not re-use)
- `sec-edgar-eval-2`: id `RGF0YXNldDoz`, 23 examples — CURRENT, correct schema
  - **Needs re-upload** after `7ccbdb3` CSV rebuild (`python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2`)
- Last Phoenix experiment on eval-2 (pre-majority-vote): `RXhwZXJpbWVudDo4` — correctness=14/23, scope=19/23, numeric=3/5

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

### `sec_edgar_get_company_fact` row fields
Every row now includes: `filing_index_url` (deterministic EDGAR archive URL), `form`, `filed`, `accession_number`. This is why BQ-15/16 can use `get_company_fact` alone (without `get_filing_metadata`) for form/date questions.

### `filing_index_url` formula (server-side, no extra HTTP call)
`https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number.replace('-','')}/"` — deterministic from accession number already in fact data.

---

## Key files

```
agents/sec_edgar_agent.yaml              ← UPDATED: Rule 6 rewritten (get_company_fact FIRST),
                                           Rule 6 "state the value alongside filing details",
                                           RESPONSE RULES: OUT OF SCOPE bullet, URL-only bullet

toolkits/sec_edgar_tools/server.py       ← filing_index_url in fact rows; REVENUE_CANDIDATES;
                                           no changes needed
toolkits/sec_edgar_tools/test_regressions.py  ← 80 assertions; all pass

eval/phoenix/run_experiment.py           ← unchanged; use --dataset-name sec-edgar-eval-2
                                           --system-prompt-version yaml
eval/phoenix/agent.py                    ← unchanged
eval/phoenix/build_dataset.py            ← builds CSV; default=sec-edgar-eval-2
eval/phoenix/create_dataset.py           ← uploads to Phoenix; run after rebuild
eval/phoenix/score_wxo_results.py        ← UPDATED: majority vote; unstable reporting;
                                           all 3 explanations on fail
eval/phoenix/datasets.yaml               ← sec-edgar-eval-2 entry
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← CURRENT (rebuilt 7ccbdb3)

eval/phoenix/judges/__init__.py          ← exports majority_vote_correctness
eval/phoenix/judges/correctness_judge.py ← UPDATED: _single_classify, _majority_vote,
                                           majority_vote_correctness, match_expected_response (3-run)
eval/phoenix/judges/relevance_judge.py   ← 3-attempt retry, judge_error return
eval/phoenix/judges/numeric_judge.py     ← deterministic: {must_include, rel_tol, max_value}
eval/phoenix/judges/sanity_check.py      ← UPDATED: 10 cases; BQ-10f numeric; BQ-17g correct;
                                           10/10 PASS (last run)
eval/phoenix/judges/fixtures/
  BQ-07f.txt    ← Apple net income FY2022–FY2026 (scope fix validation)
  BQ-09e.txt    ← Apple quarterly revenue 8 quarters (actual WXO response)
  BQ-10f.txt    ← MSFT quarterly net income 6 quarters (FY2027 Q1 label test)
  BQ-17d.txt    ← Pfizer wrong-concept response (expect incorrect)
  BQ-17g.txt    ← Pfizer CURRENT correct response (expect correct)

evaluation/run_evaluation.py             ← --ids merges into raw_results.json by id
evaluation/benchmark_questions.py        ← UPDATED: BQ-07 FY2025/FY2026 dates; BQ-10 numeric_checks;
                                           BQ-17 FY2023 mislabel guard; BQ-15/16 optional_tools
evaluation/raw_results.json              ← 23 results (all BQ-01→BQ-23); score=fail on BQ-19
                                           (stale — re-score after next run)
evaluation/EVAL_REPORT.md                ← stale (from old partial run)
evaluation/traces/                       ← BQ-01 through BQ-23 trace JSON files

docs/submission.md                       ← NEEDS final scores after Phoenix re-run
```

---

## Git log (last 10 commits)

```
7ccbdb3  fix(eval): BQ-17 FY2023 mislabel guard, BQ-10 numeric_checks, BQ-07 period-end dates
5ebd3cc  fix(agent): Rule 6 — mandate get_company_fact before get_filing_metadata for BQ-15
5aeddb0  fix(eval): majority-vote correctness judge (3-run), BQ-17g fixture, Rule 6 value mandate
5f33af1  fix(eval): BQ-14 numeric values, fiscal-year date context, routing_ok/diff, sanity f cases
d3132a4  fix(eval): judge date context, numeric no-op, sec-edgar-eval-2 dataset, agent OOS rule
ed4977b  fix(eval): remove duplicate import in run_evaluation.py; BQ-16 optional_tools
b6085ed  fix(eval): judge retry, BQ-17 alignment, filing_index_url, fixture files
6ad757d  Server-side revenue concept selection (fixes BQ-17); YAML revenue section simplified
1636e1c  Add detailed live/local tool diff script
802807b  Round 2: period labels, entity ranking, eval fixes
```

---

## Next steps (recommended order)

### 1. Re-upload sec-edgar-eval-2 dataset to Phoenix
CSV was rebuilt in `7ccbdb3` (BQ-10 now has numeric_checks → 6 Qs total):
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID
venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2
```

### 2. Run full Phoenix experiment on sec-edgar-eval-2
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
venv/bin/python eval/phoenix/run_experiment.py \
  --dataset-name sec-edgar-eval-2 \
  --system-prompt-version yaml
```
Expected improvement over last run (`RXhwZXJpbWVudDo4`: 14/23 correctness, 19/23 scope, 3/5 numeric):
- Correctness: should improve because majority vote reduces false negatives from judge flip-flopping; agent re-imported with Rule 6 fix (BQ-15)
- Numeric: now 6 questions have checks (BQ-10 added); BQ-14 values fixed

### 3. Inspect remaining failures in Phoenix UI
Open http://localhost:6006 → `sec-edgar-eval-2` → latest experiment.
Key questions to watch:
- **BQ-15** (filing attribution): did Rule 6 fix cause agent to call `get_company_fact` first?
- **BQ-13** (compare 3 companies): unstable — are all 3 companies present in response?
- **BQ-10** (MSFT quarterly): does the agent return single-quarter (not YTD) values?

### 4. Run score_wxo_results.py for a quick local re-score
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID JUDGE_MODEL
venv/bin/python eval/phoenix/score_wxo_results.py
```

### 5. Update docs/submission.md with final scores
Once the Phoenix experiment completes, fill in the score table.

### 6. Merge fixes-round2 → main
```bash
git checkout main && git merge fixes-round2 && git push origin main
```

---

## Skills to activate

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns (`.bob/skills/mcp-eval-wxai/SKILL.md`)
