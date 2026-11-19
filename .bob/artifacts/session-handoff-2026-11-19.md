# SEC EDGAR Project — Session Handoff (2026-11-19, end of session 5)

Read this file first before doing any work in a new session.

---

## Project in one sentence

An 11-tool FastMCP server (`sec_edgar_tools`) deployed to IBM Code Engine that
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
| Phoenix server | Running on this VM — UI at http://localhost:6006 — check: `ss -tlnp \| grep 6006` |
| Phoenix run command | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL && venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml` |
| Run evaluator (no Phoenix) | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID JUDGE_MODEL && venv/bin/python eval/phoenix/score_wxo_results.py` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` |
| Active branch | `main` at `d78f787` |
| Last commit | `d78f787` — "feat(server): add sec_edgar_full_text_search tool (11th tool, 17 tests)" |
| Release tag | `v1.1.0` → `752e86d` (last tagged; session 5 not yet tagged) |
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
| M7 — docs/submission.md final scores | ✅ Complete | 22/23 correct, 1 unstable, 23/23 scope, 8/8 numeric |
| M8 — Doc accuracy corrections | ✅ Complete | 13-point review applied to both submission.md and interpretation.md |
| M9 — Phoenix re-run on sec-edgar-eval-2 | ✅ Complete | Experiment 11 run; 23/23 tasks; dataset expected answers corrected |
| M10 — BQ-19 routing fix | ✅ Complete | expected_tools=[] (non-deterministic tool choice; both valid) |
| M11 — Merge fixes-round2 → main + push | ✅ Complete | Both branches at `329b46c`; pushed to origin |
| M12 — Optional cleanup + v1.0.0 tag | ✅ Complete | 22/23 score confirmed; dataset fixed; tag pushed |
| M13 — BQ-20 pass_criteria fix | ✅ Complete | EPS range updated; BQ-20 now unanimous correct |
| M14 — sec_edgar_resolve_synonym tool | ✅ Complete | 75 synonyms, 22 regression tests; commit `b9900a5` |
| M15 — companyfacts 24h TTL cache | ✅ Complete | _fetch_company_facts helper; 4 call sites; commit `752e86d` |
| M16 — sec_edgar_get_filing_text tool | ✅ Complete | HTML text extraction, TOC-skip heuristic, 18 tests; commit `8f1a439` |
| M17 — Global SEC rate limiter | ✅ Complete | asyncio.Semaphore(8) via _edgar_get(); all 6 callsites; commit `20c9357` |
| M18 — sec_edgar_full_text_search tool | ✅ Complete | EFTS keyword search, 17 tests; commit `d78f787` |

---

## This session's changes (session 5)

### Commits

```
d78f787  feat(server): add sec_edgar_full_text_search tool (11th tool, 17 tests)  ← HEAD
20c9357  perf(server): add global SEC rate limiter (asyncio.Semaphore(8))
8f1a439  feat(server): add sec_edgar_get_filing_text tool (10th tool, 18 tests)
752e86d  perf(server): add 24h TTL cache for companyfacts JSON  ← v1.1.0
```

### sec_edgar_get_filing_text (`8f1a439`)

New 10th tool in `toolkits/sec_edgar_tools/server.py`:
- **Input**: `identifier` + `accession_number` (required); `section` hint + `max_chars` (optional, default 8000, max 32000).
- **Flow**: resolves primary document from `submissions.json` cache; falls back to `index.json` for older filings. Fetches the HTML document, strips tags with `_strip_html()`, returns plain text.
- **Section seeking** (`_find_section_offset`): walks up to 4 occurrences of a section keyword and picks the first whose following 400-char window matches `_PROSE_PERIOD_RE` (`[a-z]\. [A-Z]`) — skips Table of Contents entries.
- **Supported sections**: `risk_factors`, `mda`, `business`, `financials`, `legal`, `controls`, `8k_items`.
- **Return keys**: company, cik, accession_number, form, filing_date, primary_document, section_sought, section_offset, text, truncated, document_url.
- Zero new dependencies (uses `re` already imported).
- 18 new regression tests (test 17) — all pass.

### Global rate limiter (`20c9357`)

- New `_edgar_sem` / `_get_sem()` / `_edgar_get()` infrastructure.
- `asyncio.Semaphore(8)` — permits ≤ 8 concurrent in-flight EDGAR requests (< 10 req/s limit).
- Semaphore is per-event-loop (same rebuild pattern as `_http_client`).
- All 6 outbound HTTP callsites replaced: `_ensure_ticker_cache`, `_search_all_filers`, `_fetch_submission`, `_fetch_company_facts`, `sec_edgar_get_filing_text` (index.json + document).
- Cleaned up orphaned `client` parameter from `_ensure_ticker_cache` and `_search_all_filers`; removed orphaned `client = _get_client()` lines.

### sec_edgar_full_text_search (`d78f787`)

New 11th tool in `toolkits/sec_edgar_tools/server.py`:
- **Input**: `query` (required); `forms` (comma-sep, e.g. `"10-K"`); `start_date`/`end_date` (YYYY-MM-DD); `identifier` (ticker/CIK scope); `limit` (1–40, default 10).
- **Backend**: `efts.sec.gov/LATEST/search-index` — same EFTS endpoint used by `_search_all_filers` but exposed as a user-facing tool for content keyword search.
- **Return keys**: query, forms, total_matches, results (list of accession_number, form, filing_date, period_ending, company, ticker, cik, filing_index_url).
- Reuses `_parse_display_name` for EFTS `display_names` → company/ticker/CIK.
- Note: `forms=10-K` returns both `10-K` and `10-K/A` (EDGAR EFTS behavior).
- 17 new regression tests (test 18) — all pass.

---

## Current evaluation state (canonical — `score_wxo_results.py`, 2026-11-19)

```
correctness=23/23  (BQ-20 unanimous correct after pass_criteria fix)
scope=23/23
numeric=8/8 (of 8 with checks)
```

EVAL_REPORT.md (23/23 all-pass, run 2026-11-19 03:04 against live WXO) = canonical truth.

**Important**: The 3 new tools (get_filing_text, full_text_search) and the rate limiter
are NOT yet deployed to Code Engine and NOT yet imported into WXO. The deployed server
is still at v1.1.0 (9 tools). The eval scores above reflect the v1.1.0 agent.

### Phoenix datasets:
- `sec-edgar-eval-1`: id `RGF0YXNldDoy`, 23 examples — OLD schema (do not re-use)
- `sec-edgar-eval-2`: id `RGF0YXNldDoz`, 23 examples — CURRENT, correct schema
  - Most recent upload: 2026-11-19 (session 3, with corrected reference answers)
  - Experiment 11 (`RXhwZXJpbWVudDoxMQ==`) is the latest run

---

## Git log (last 8 commits)

```
d78f787  feat(server): add sec_edgar_full_text_search tool (11th tool, 17 tests)  ← HEAD
20c9357  perf(server): add global SEC rate limiter (asyncio.Semaphore(8))
8f1a439  feat(server): add sec_edgar_get_filing_text tool (10th tool, 18 tests)
752e86d  perf(server): add 24h TTL cache for companyfacts JSON  ← v1.1.0
b9900a5  feat(server): add sec_edgar_resolve_synonym tool (75 synonyms, 22 tests); fix BQ-20 pass_criteria
fd0a132  chore: session handoff 2026-11-19 (session 3 complete — v1.0.0 tagged, 22/23 score)
e604b36  chore(eval): update scores to 22/23; fix Phoenix dataset stale expected answers  ← v1.0.0
329b46c  fix(eval): BQ-19 expected_tools → [] (fictitious-ticker refusal; tool non-deterministic)
```

Tags: `v1.0.0` → `e604b36`, `v1.1.0` → `752e86d`

---

## Key files

```
agents/sec_edgar_agent.yaml              ← UPDATED (a57eebf): Rule 6 value-first mandate;
                                           Rule 8 Q4 derived rows; re-imported (b8c4961 run confirms)
                                           NOTE: not yet updated for new tools (get_filing_text,
                                           full_text_search) — agent instructions may need updating
                                           after CE deploy.

toolkits/sec_edgar_tools/server.py       ← UPDATED (d78f787):
                                           - 11 tools total (up from 9 at v1.1.0)
                                           - sec_edgar_get_filing_text (tool 10, 8f1a439)
                                           - sec_edgar_full_text_search (tool 11, d78f787)
                                           - _edgar_get() rate limiter (20c9357)
                                           - sec_edgar_resolve_synonym tool (b9900a5)
                                           - _fetch_company_facts with 24h TTL cache (752e86d)
                                           - Q4 derivation in sec_edgar_get_quarterly_facts
                                           - derived/derivation fields; filing_index_url; REVENUE_CANDIDATES
toolkits/sec_edgar_tools/requirements.txt ← PINNED (2966d5e): fastmcp==4.1.3, httpx==0.28.1, pydantic==2.14.3
toolkits/sec_edgar_tools/test_regressions.py ← 72 assertions (tests 16/17/18 added session 5); all pass

eval/phoenix/run_experiment.py           ← unchanged; use --dataset-name sec-edgar-eval-2
                                           --system-prompt-version yaml
eval/phoenix/agent.py                    ← unchanged
eval/phoenix/build_dataset.py            ← UPDATED (e604b36): reference answers corrected for
                                           BQ-04/07/08/13/17/20 (FY2025/26 allowances; SIC fix)
eval/phoenix/create_dataset.py           ← uploads to Phoenix; run after rebuild
eval/phoenix/score_wxo_results.py        ← majority vote; unstable reporting; all 3 explanations on fail
eval/phoenix/datasets.yaml              ← sec-edgar-eval-2 entry
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← UPDATED (e604b36)

eval/phoenix/judges/__init__.py          ← exports majority_vote_correctness
eval/phoenix/judges/correctness_judge.py ← _single_classify, _majority_vote, majority_vote_correctness
eval/phoenix/judges/relevance_judge.py   ← 3-attempt retry, judge_error return
eval/phoenix/judges/numeric_judge.py     ← deterministic: {must_include, rel_tol, max_value}
eval/phoenix/judges/sanity_check.py      ← 11 cases; BQ-10h; expect_correctness guard; 11/11 PASS

evaluation/run_evaluation.py             ← --ids merges into raw_results.json by id
evaluation/benchmark_questions.py        ← UPDATED (b9900a5): BQ-20 pass_criteria EPS range fixed;
                                           BQ-19 expected_tools=[]
evaluation/raw_results.json              ← 23 results (all BQ-01→BQ-23, refreshed 329b46c)
evaluation/traces/                       ← BQ-01 through BQ-23 trace JSON files (current as of 329b46c)
evaluation/EVAL_REPORT.md                ← 23/23 pass, run 2026-11-19 03:04

docs/submission.md                       ← UPDATED (e604b36): 22/23 score; 2026-11-19 date
evaluation/interpretation.md             ← UPDATED (e604b36): same corrections
```

---

## Known remaining gaps / future work (low priority)

1. **Deploy new tools to Code Engine** — `sec_edgar_get_filing_text` and
   `sec_edgar_full_text_search` are built and tested locally but not yet deployed.
   Run the CE deploy command (see environment facts) then re-import the toolkit in WXO.
   After deploy, consider updating the agent instructions to guide tool selection.

2. **Agent instructions update** — `agents/sec_edgar_agent.yaml` has no mention of
   the two new tools. Add routing rules for narrative/qualitative questions
   (→ `get_filing_text`) and keyword-across-filings questions (→ `full_text_search`).

3. **Tag v1.2.0** — the three session-5 commits deserve a release tag after CE deploy.

4. **sec_edgar_get_insider_transactions** — Form 4 insider buy/sell data.
   `edgar_ownership` in edgartools shows the pattern. Medium effort, interesting use case.

5. **8-K earnings release tool** — cross-check Q4 derived values. Very low priority.

6. **Synonym table expansion** — `_SYNONYM_TABLE` easy to extend; zero deploy risk.

7. **sec_edgar_screen** — discover companies by SIC code/exchange/state. Zero network
   calls (local reference data). Low effort.

---

## Discoveries (critical for new sessions)

### WXO token refresh pattern (MUST use `--api-key` flag)
`orchestrate env activate gsa-hackathon` without `--api-key` reads from stdin — in a
non-interactive session it gets empty string → IBM IAM 400. Always use:
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
```

### _edgar_get() — rate-limited HTTP wrapper (session 5)
All outbound SEC calls now go through `_edgar_get(url, **kwargs)` which acquires
`_edgar_sem` (Semaphore(8)) before calling `_get_client().get(...)`. Never call
`client.get(...)` directly — use `_edgar_get()` for any new EDGAR HTTP calls.

### sec_edgar_get_filing_text — section seeking
- `_find_section_offset(text, section)` walks up to 4 occurrences of each keyword
  and picks the first whose 400-char context matches `_PROSE_PERIOD_RE` (`[a-z]\. [A-Z]`).
- This skips Table of Contents entries (which have section numbers like "Item 1B." but
  not prose sentences). Best-effort — may still land in forward-looking disclaimer text.
- Supported `section` hints: `risk_factors`, `mda`, `business`, `financials`, `legal`,
  `controls`, `8k_items`.

### sec_edgar_full_text_search — EFTS behavior
- Endpoint: `efts.sec.gov/LATEST/search-index?q=...`
- `forms=10-K` returns both `10-K` and `10-K/A` (amended) — this is correct EDGAR behavior.
- `entity=` param accepts CIK (numeric string); ticker resolution done via `_TICKER_CACHE`.
- `total_matches` is the full EDGAR count; results are capped at `limit` (max 40).

### Majority-vote judge (`correctness_judge.py`)
- `majority_vote_correctness(q, r, ref)` → 3 runs → majority label
- Returns: `label`, `score`, `explanation`, `all_explanations: list[str]`, `stable: bool`
- `unstable` = 2-of-3 split → `score=0.5`
- `match_expected_response()` (Phoenix) strips `all_explanations`/`stable`
- `score_wxo_results.py` prints all 3 explanations for unstable/incorrect

### Phoenix experiment API (arize-phoenix-client 3.7.0)
- `Client(base_url=phoenix_endpoint)` — not `Client(endpoint=...)`
- Numeric judge metadata: Phoenix passes `{"metadata": "<json-str>"}` envelope —
  must do `json.loads(metadata["metadata"])` to get `numeric_checks`
- `c.datasets.list()` returns `list[dict]`; use GraphQL for experiment details
- Annotation names: `"correctness"`, `"scope"`, `"numeric_accuracy"`
- GraphQL endpoint at `/graphql`

### Phoenix scores vs score_wxo_results.py (known gap)
Phoenix uses fresh live Llama-agent responses + a judge lacking date-context injection.
The `score_wxo_results.py` harness uses `raw_results.json` (cached production WXO
responses) with the full date-aware prompt. Phoenix will consistently score lower for
FY2025/2026 questions. Canonical metric = `score_wxo_results.py`.

### Q4 derivation (server-side, `sec_edgar_get_quarterly_facts`)
- Finds annual FY (fp=FY, 10-K, 350–380 days) and nine-month YTD (fp=Q3, 260–285 days)
  sharing same `period_start`
- Q4 = annual − nine-month YTD; derived rows: `derived=True`, `derivation="..."`
- Only for `best_unit == "USD"` and flow items (obs have `start` date)
- Skipped for `USD/shares`, `shares`, or instant facts (no `start`)

### companyfacts TTL cache (`_fetch_company_facts`)
- `_FACTS_CACHE: dict[str, tuple[dict, float]]` — keyed by padded CIK
- TTL check: `time.monotonic() - fetched_at < 86400.0`
- Cache is per-process (in-memory); Code Engine multi-instance deployments each
  have their own cache — no cross-instance sharing. This is fine for latency
  reduction within a session; not a correctness concern.

### sec_edgar_resolve_synonym
- `_SYNONYM_TABLE` keyed by lowercase alias; value `{canonical_name, ticker, note}`
- Input normalisation: `.strip().lower().rstrip(".,;:!?")`
- Returns `{input, canonical_name, ticker, note}` on hit; `{error, hint, input}` on miss
- Zero network calls — purely a dict lookup; `openWorldHint: False`

---

## Next steps (suggested order for next session)

1. **(High priority) Deploy to Code Engine** — the 3 session-5 commits are not live.
   Run CE deploy, re-import toolkit in WXO, smoke-test the new tools via chat.

2. **(High priority) Update agent instructions** — add routing rules for
   `sec_edgar_get_filing_text` and `sec_edgar_full_text_search` to `sec_edgar_agent.yaml`.

3. **(Medium) Tag v1.2.0** after successful CE deploy.

4. **(Medium) sec_edgar_get_insider_transactions** — Form 4 data.

5. **(Low) Synonym table expansion**, `sec_edgar_screen`, 8-K earnings tool.

---

## Skills to activate in a fresh session

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns
