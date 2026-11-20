# SEC EDGAR Project — Session Handoff (2026-11-20, end of session 7)

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
| Active branch | `main` at `77a9353` |
| Last commit | `77a9353` — "feat(eval): add BQ-24–BQ-27 covering get_filing_text and full_text_search; 27/27 pass (100%)" |
| Release tag | `v1.2.0` → `ed168e7` (latest; pushed to origin) |
| WXO instance ID | `76b76ce7-8b9e-4f7e-885b-967fbaef80c9` |
| WXO agent ID | `dd7fadae-34b2-478b-98c4-2fc48cbd35e5` (sec_edgar_agent) |
| Re-import toolkit | `venv/bin/orchestrate toolkits remove --name sec_edgar_tools && venv/bin/orchestrate toolkits add --kind mcp --name sec_edgar_tools --description "SEC EDGAR toolkit: company lookup, filing history, and XBRL financial-statement facts from the SEC's public APIs." --url "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp" --transport streamable_http --tools "*"` |
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
| M19 — CE deploy v1.2.0 + toolkit/agent re-import | ✅ Complete | 11 tools live on CE; toolkit re-imported; agent re-imported; commit `ed168e7` |
| M20 — Agent routing rules for all 11 tools | ✅ Complete | Rule 0 (resolve_synonym), Rule 9 (get_filing_text), Rule 10 (full_text_search); smoke-tested 3/3 pass |
| M21 — Eval dataset extended to 27 Qs | ✅ Complete | BQ-24–BQ-27 (filing_text × 2, full_text_search × 2); 27/27 pass; commit `77a9353` |

---

## This session's changes (session 7)

### Commits

```
77a9353  feat(eval): add BQ-24–BQ-27 covering get_filing_text and full_text_search; 27/27 pass  ← HEAD
a09cba7  chore: session handoff 2026-11-19 (session 6 complete)
```

Session 7 work: extended eval dataset with 4 new BQs (BQ-24–BQ-27) covering
`sec_edgar_get_filing_text` and `sec_edgar_full_text_search`; rebuilt CSV (27 rows);
ran all 4 against live agent (27/27 total, 100% pass); updated EVAL_REPORT.md.
Also added `sec_edgar_resolve_synonym`, `sec_edgar_get_filing_text`,
`sec_edgar_full_text_search` to `ALL_TOOL_NAMES` in `run_evaluation.py`.

---

## Previous session's changes (session 6)

### Commits

```
ed168e7  feat(agent): add routing rules for 3 new tools; 11 tools total  ← v1.2.0
64d30ab  chore: session handoff 2026-11-19 (session 5 complete)
```

Session 6 work: CE deploy of the 3 session-5 commits, toolkit re-import (8 → 11 tools),
agent YAML update (routing rules + tools list + 2 starter prompts), smoke-test 3/3 pass,
v1.2.0 tag pushed.

---

## Previous session's changes (session 5)

### Commits

```
d78f787  feat(server): add sec_edgar_full_text_search tool (11th tool, 17 tests)
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

## Current evaluation state (canonical — `run_evaluation.py`, 2026-11-20)

```
score=27/27 pass  (100%)  partial=0  fail=0
```

`evaluation/EVAL_REPORT.md` (27/27 all-pass, run 2026-11-20 22:29 against live WXO) = canonical truth.

**Note**: `score_wxo_results.py` uses `raw_results.json` (cached WXO responses) with the
majority-vote LLM judge. The last full run of `score_wxo_results.py` covered BQ-01–BQ-23
only (session 6). After next Phoenix re-run, run `score_wxo_results.py` over all 27 Qs.

**Phoenix dataset**: sec-edgar-eval-2 in Phoenix still has 23 rows (not yet updated with
BQ-24–BQ-27). The local CSV at `eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv`
has 27 rows — run `create_dataset.py` to upload before the next Phoenix experiment.

### Phoenix datasets:
- `sec-edgar-eval-1`: id `RGF0YXNldDoy`, 23 examples — OLD schema (do not re-use)
- `sec-edgar-eval-2`: id `RGF0YXNldDoz`, 23 examples in Phoenix — **stale** (CSV has 27)
  - Most recent upload: 2026-11-19 (session 3, with corrected reference answers)
  - Experiment 11 (`RXhwZXJpbWVudDoxMQ==`) is the latest run
  - **Before next Phoenix run**: upload new CSV → `python create_dataset.py --dataset-name sec-edgar-eval-2`

---

## Git log (last 8 commits)

```
77a9353  feat(eval): add BQ-24–BQ-27; 27/27 pass (100%)  ← HEAD, main
a09cba7  chore: session handoff 2026-11-19 (session 6 complete)
ed168e7  feat(agent): add routing rules for 3 new tools; 11 tools total  ← v1.2.0
64d30ab  chore: session handoff 2026-11-19 (session 5 complete — 11 tools, 72 tests)
d78f787  feat(server): add sec_edgar_full_text_search tool (11th tool, 17 tests)
20c9357  perf(server): add global SEC rate limiter (asyncio.Semaphore(8))
8f1a439  feat(server): add sec_edgar_get_filing_text tool (10th tool, 18 tests)
752e86d  perf(server): add 24h TTL cache for companyfacts JSON  ← v1.1.0
```

Tags: `v1.0.0` → `e604b36`, `v1.1.0` → `752e86d`, `v1.2.0` → `ed168e7`

---

## Key files

```
agents/sec_edgar_agent.yaml              ← UPDATED (ed168e7): 11 tools in tools: list;
                                           Rule 0 (resolve_synonym), Rule 6 value-first,
                                           Rule 8 Q4 derived rows, Rule 9 (get_filing_text),
                                           Rule 10 (full_text_search); 12 starter prompts;
                                           re-imported and smoke-tested 3/3 (session 6).
                                           Will need new rules for tools added in session 8.

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
eval/phoenix/build_dataset.py            ← UPDATED (77a9353): BQ-24–BQ-27 reference answers added
eval/phoenix/create_dataset.py           ← uploads to Phoenix; run after rebuild
eval/phoenix/score_wxo_results.py        ← majority vote; unstable reporting; all 3 explanations on fail
eval/phoenix/datasets.yaml              ← sec-edgar-eval-2 entry
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← UPDATED (77a9353): 27 rows

eval/phoenix/judges/__init__.py          ← exports majority_vote_correctness
eval/phoenix/judges/correctness_judge.py ← _single_classify, _majority_vote, majority_vote_correctness
eval/phoenix/judges/relevance_judge.py   ← 3-attempt retry, judge_error return
eval/phoenix/judges/numeric_judge.py     ← deterministic: {must_include, rel_tol, max_value}
eval/phoenix/judges/sanity_check.py      ← 11 cases; BQ-10h; expect_correctness guard; 11/11 PASS

evaluation/run_evaluation.py             ← UPDATED (77a9353): ALL_TOOL_NAMES has all 11 tools;
                                           --ids merges into raw_results.json by id
evaluation/benchmark_questions.py        ← UPDATED (77a9353): 27 Qs, 13 categories, all 11 tools;
                                           BQ-24–BQ-27 added (filing_text, full_text_search)
evaluation/raw_results.json              ← 27 results (BQ-01→BQ-27, run 2026-11-20)
evaluation/traces/                       ← BQ-01 through BQ-27 trace JSON files
evaluation/EVAL_REPORT.md                ← 27/27 pass, run 2026-11-20 22:29

docs/submission.md                       ← UPDATED (e604b36): 22/23 score; 2026-11-19 date
evaluation/interpretation.md             ← UPDATED (e604b36): same corrections
```

---

## Known remaining gaps / future work

**In scope (session 8 — do in this order):**

1. **Synonym table expansion** — zero deploy risk; extend `_SYNONYM_TABLE` in `server.py`
   with more brand names. No CE deploy needed if synonyms already match common queries.
   Commit + regression test.

2. **`sec_edgar_screen`** — new tool to discover companies by SIC code, exchange, or state
   of incorporation. Use the SEC's company_tickers.json + submissions JSON (local/cached).
   Zero network calls beyond the ticker cache. Add regression tests. No CE deploy needed
   until a tool function is added.

3. **8-K earnings release tool** — fetch the 8-K press release for a company and extract
   key earnings figures (EPS, revenue) to cross-check Q4 derived values. Requires EDGAR
   network call (HTML/text extraction, similar to `get_filing_text`). After implementing:
   - Add regression tests
   - CE deploy (`ibmcloud ce app update …`)
   - Re-import toolkit + agent YAML update (new routing rule)
   - Add BQs to eval dataset, run against live agent

**After all three tools done:**

4. **Phoenix re-run** — upload new 27-row CSV (`python create_dataset.py`) then run
   `run_experiment.py`. Covers all 27+ BQs including the 4 new ones.
   Also run `score_wxo_results.py` over all 27 results for the LLM-judge canonical score.

**Out of scope (dropped):**

5. ~~**sec_edgar_get_insider_transactions**~~ — Form 4 data; outside the 10-K/10-Q/8-K
   design scope. Dropped.

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

## Next steps (suggested order for session 8)

1. **Synonym table expansion** — extend `_SYNONYM_TABLE` in `server.py`; add regression
   tests; commit. No CE deploy needed.

2. **`sec_edgar_screen` tool** — discover companies by SIC code/exchange/state using
   the cached SEC ticker/submissions data. No new network calls. Add regression tests;
   commit. Needs CE deploy + toolkit re-import + agent YAML routing rule.

3. **8-K earnings release tool** — parse 8-K press release HTML via `get_filing_text`
   pattern. Add regression tests; commit. Needs CE deploy + toolkit re-import + agent
   YAML routing rule.

4. Add BQs for `sec_edgar_screen` and 8-K tool; run `run_evaluation.py --ids <new>`.

5. **Phoenix re-run** — upload updated 27+ row CSV, run `run_experiment.py` over full
   dataset. Run `score_wxo_results.py` for canonical LLM-judge score.

---

## Skills to activate in a fresh session

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns
