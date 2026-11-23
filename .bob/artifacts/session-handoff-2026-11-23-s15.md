# SEC EDGAR Project — Session Handoff (2026-11-23, end of session 15)

Read this file first before doing any work in a new session.

---

## Project in one sentence

A 14-tool FastMCP server (`sec_edgar_tools`) deployed to IBM Code Engine that
lets an IBM watsonx Orchestrate agent (`sec_edgar_agent`) answer questions about
SEC filings and XBRL financial data for any publicly traded company.

---

## Environment facts

| Item | Value |
|---|---|
| Workspace | `/home/itzuser/wxo-agentic-workflow/` |
| Venv | `./venv/` — Python 3.12 |
| arize-phoenix | 21.0.0 — always use `venv/bin/python`, never system `python` |
| arize-phoenix-client | 3.7.0 |
| WXO environment | `gsa-hackathon` — IBM Cloud Toronto (`ca-tor`) |
| WXO token refresh | `source .env && export WXO_API_KEY && venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |
| Re-import agent | `venv/bin/orchestrate agents import -f agents/sec_edgar_agent.yaml` |
| Code Engine project | `ce-550000w6t0` — resource group `eid-6ac40a21a8799c11a48dc107` |
| CE app URL | `https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp` |
| CE login | `ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default` then `ibmcloud target -g eid-6ac40a21a8799c11a48dc107` then `ibmcloud ce project select --name ce-550000w6t0` |
| CE deploy command | `ibmcloud ce app update --name sec-edgar-tools-mks --build-source toolkits/sec_edgar_tools --build-dockerfile Dockerfile` |
| **CR quota** | **Free the trash before each deploy**: `ibmcloud cr region-set us-south && ibmcloud cr image-prune-untagged --restrict gsa-hackathon-cr-student7 --force` then restore+delete trash items if still over. See session 14 notes. |
| watsonx.ai URL | `https://ca-tor.ml.cloud.ibm.com` |
| watsonx.ai project ID | `2d244f0a-a04f-4585-b4eb-94da0b59541a` |
| Phoenix server | Running on this VM — UI at http://localhost:6006 — check: `ss -tlnp \| grep 6006` |
| Phoenix run command | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL && venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml` |
| **Rebuild dataset first** | `source .env && venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2` (Phoenix server stores old version; must re-upload after adding BQs) |
| Run evaluator (no Phoenix) | `source .env && export WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID && venv/bin/python evaluation/run_evaluation.py` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` |
| Active branch | `main` at `8f34ffe` |
| Last commit | `8f34ffe` — "feat(eval): add BQ-38 EBITDA derived-metric benchmark; add XBRL ratio overrides (ROE, D/E, P/E, asset turnover, BVPS); 359 regression assertions" |
| WXO instance ID | `76b76ce7-8b9e-4f7e-885b-967fbaef80c9` |
| WXO agent ID | `dd7fadae-34b2-478b-98c4-2fc48cbd35e5` (sec_edgar_agent) |
| Re-import toolkit | `venv/bin/orchestrate toolkits add --kind mcp --name sec_edgar_tools --description "SEC EDGAR toolkit: company lookup, filing history, and XBRL financial-statement facts from the SEC's public APIs." --url "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp" --transport streamable_http --tools "*"` |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |
| Active model vars | `AGENT_MODEL=meta-llama/llama-3-3-70b-instruct` / `JUDGE_MODEL=mistralai/mistral-small-3-1-24b-instruct-2503` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1–M47 | ✅ Complete | See session-14 handoff for details |
| M48 — BQ-38 EBITDA derived-metric benchmark | ✅ Complete | 38/38 pass; commit `8f34ffe` |
| M49 — XBRL ratio overrides (ROE/D-E/P-E/asset turnover/BVPS) | ✅ Complete | 95 total canonical entries, 14 derived-hint keys; commit `8f34ffe` |
| M50 — Regression test runner fix (async XBRL tests now run) | ✅ Complete | 359 assertions, all pass; commit `8f34ffe` |

---

## This session's changes (session 15)

### Commits

```
8f34ffe  feat(eval): add BQ-38 EBITDA derived-metric benchmark; add XBRL ratio overrides; 359 regression assertions  ← HEAD, v1.7.0+
5178931  feat(server): add XBRL derived-metric hints and new ADR synonyms; 291 regression assertions  (previous HEAD)
```

### What changed in session 15

1. **BQ-38 — EBITDA derived-metric benchmark** (`8f34ffe`):
   - Added to `evaluation/benchmark_questions.py` as category `xbrl_derived_metric` (category 19), difficulty hard
   - Question: "What was Apple's EBITDA for fiscal year 2026? Use XBRL data to calculate it from its components."
   - Expected tools: `sec_edgar_resolve_xbrl_concept` → `sec_edgar_get_company_fact` ×2+
   - `_REFERENCE_ANSWERS["BQ-38"]` added to `eval/phoenix/build_dataset.py`
   - Phoenix CSV rebuilt to 38 rows
   - Evaluated: BQ-38 ✅ PASS — agent called `resolve_xbrl_concept`, received derivation_note, then called `get_company_fact` ×3
   - Full eval: **38/38 pass (100%)**

2. **Additional XBRL ratio overrides** (`8f34ffe`):
   Added to both `_DERIVED_HINTS` and `_CANONICAL` in `server.py`:
   - `return on equity` / `roe` → NetIncomeLoss + StockholdersEquity
   - `debt to equity` / `debt-to-equity` → Liabilities + StockholdersEquity
   - `price to earnings` / `pe ratio` / `p/e ratio` → EarningsPerShareDiluted + EarningsPerShareBasic (with note: share price NOT in EDGAR)
   - `asset turnover` → Revenues + Assets
   - `book value per share` → StockholdersEquity + CommonStockSharesOutstanding
   - `_CANONICAL` table: 80 → 95 entries
   - `_DERIVED_HINTS` table: 3 → 14 keys (including hyphen variants)

3. **Regression test runner fix** (`8f34ffe`):
   - `test_xbrl_concept_resolver()` converted from `def` to `async def` (was calling async
     `sec_edgar_resolve_xbrl_concept` synchronously — all XBRL assertions were dead code)
   - Added `await` to all 25 `sec_edgar_resolve_xbrl_concept` calls in the function
   - Added `await test_xbrl_concept_resolver()` call in `main()` so it runs inside `asyncio.run()`
   - Removed `sys.exit()` from inside `main()` (it was silently killing the process before
     the XBRL tests could run); moved final exit to `__main__` block
   - New assertion count: **291 → 359** (68 previously-dead XBRL assertions now run)
   - All 359 assertions pass

4. **CE deploy**: NOT needed this session. `server.py` XBRL changes are purely
   in-process data structures (Python dicts inside the function body) — no code path
   change, only new dict entries. The deployed container at `v1.7.0` already serves
   these queries correctly because:
   - `_DERIVED_HINTS` / `_CANONICAL` are defined inside the function and re-evaluated
     each call — not module-level constants
   - **Wait**: Actually these dicts ARE module-level in this context (defined inside
     the tool function body, re-instantiated each call). The deployed binary doesn't
     have the new entries. **A CE redeploy IS needed to make new derived-hint keys live.**
   - See "CE deploy needed" note below.

---

## ⚠️ CE REDEPLOY NEEDED

Session 15 added new `_DERIVED_HINTS` and `_CANONICAL` entries to `server.py`. These
are only in the workspace `HEAD` (`8f34ffe`), not in the live container (`v1.7.0` / `5178931`).

**Before deploying, run the CR quota cleanup:**
```bash
ibmcloud cr region-set us-south
ibmcloud cr image-prune-untagged --restrict gsa-hackathon-cr-student7 --force
ibmcloud cr quota
```

If still over quota after pruning untagged images, restore-then-delete the trash items:
```bash
ibmcloud cr trash-list --restrict gsa-hackathon-cr-student7 2>&1 | grep "us.icr.io" | \
  awk '{print $1}' > /tmp/trash.txt
while IFS= read -r d; do
    ibmcloud cr image-restore "$d" 2>&1 | tail -1
    ibmcloud cr image-rm "$d" 2>&1 | tail -1
done < /tmp/trash.txt
```

**Then deploy:**
```bash
source .env && export IBMCLOUD_API_KEY
ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default
ibmcloud target -g eid-6ac40a21a8799c11a48dc107
ibmcloud ce project select --name ce-550000w6t0
ibmcloud ce app update --name sec-edgar-tools-mks --build-source toolkits/sec_edgar_tools --build-dockerfile Dockerfile
```

After deploy, tag the new version and smoke-test BQ-38 and BQ-34/BQ-35.

---

## Current evaluation state (canonical — `run_evaluation.py`)

**38/38 pass (100%)** — last run 2026-11-23, commit `8f34ffe`.

---

## Git log (last 8 commits)

```
8f34ffe  feat(eval): add BQ-38 EBITDA derived-metric benchmark; add XBRL ratio overrides; 359 regression assertions  ← HEAD, main
5178931  feat(server): add XBRL derived-metric hints and new ADR synonyms; 291 regression assertions  v1.7.0
b19c544  docs: update submission.md and interpretation.md to 37 BQs, v1.6.0, Exp 18
ef820ce  chore: update s13 handoff — M41 BQ-37 complete, 37/37, v1.6.0, session 14 start updated
c0cf335  feat(eval): add BQ-37 4-company compare_companies stress test; 37/37 pass (100%)  v1.6.0
f572684  chore: update s13 handoff — CE deploy done, M40 complete
1cfc4f3  chore: session handoff 2026-11-23 (session 13 complete)
58e9d9c  feat(eval): add BQ-36 xbrl_concept_chain (resolve→compare deferred revenue)  v1.5.0
```

Tags: `v1.0.0`–`v1.4.0` (earlier), `v1.5.0` → `58e9d9c`, `v1.6.0` → `c0cf335`, `v1.7.0` → `5178931`

**Note**: `8f34ffe` is untagged — tag as `v1.8.0` after CE redeploy and smoke test.

---

## Key files

```
agents/sec_edgar_agent.yaml              ← 14 tools; Rules 0–13; "fourteen tools" in instructions
                                           Current in WXO (re-imported session 12)

toolkits/sec_edgar_tools/server.py       ← 14 tools; _SYNONYM_TABLE 198 entries; _CANONICAL 95 entries;
                                           _DERIVED_HINTS 14 keys; early-exit path for derived metrics
toolkits/sec_edgar_tools/xbrl_concepts_data.py  ← 7,462 FASB US-GAAP 2026 concepts (generated)
toolkits/sec_edgar_tools/Dockerfile      ← COPY includes xbrl_concepts_data.py
toolkits/sec_edgar_tools/test_regressions.py    ← 21 test functions, 359 assertions; all pass

evaluation/run_evaluation.py             ← supports any_of_tools field
evaluation/benchmark_questions.py        ← 38 Qs; 19 categories; BQ-38 = xbrl_derived_metric
evaluation/raw_results.json              ← 38 results (38/38 pass, run 2026-11-23)
evaluation/EVAL_REPORT.md                ← 38/38 pass, run 2026-11-23

eval/phoenix/build_dataset.py            ← _REFERENCE_ANSWERS for BQ-01–BQ-38
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← 38 rows

docs/submission.md                       ← updated through session 14 (37 BQs, v1.7.0, Exp 18) — NEEDS UPDATE
evaluation/interpretation.md             ← updated through session 14 — NEEDS UPDATE
```

---

## Discoveries (critical for new sessions)

### test_regressions.py XBRL tests are now async
`test_xbrl_concept_resolver()` is now `async def` and called from `main()`.
If you add new XBRL concept tests, add them to `test_xbrl_concept_resolver()` with `await`.
The old `test_multi_event_loop()` still runs synchronously after `asyncio.run(main())`.

### Dockerfile must list all Python files explicitly
`COPY server.py app.py xbrl_concepts_data.py ./` — if a new Python module is added to the
toolkit, it MUST be added to this COPY line or the container will crash on import.

### any_of_tools scoring field
`evaluation/run_evaluation.py` supports `any_of_tools: [t1, t2]` in a benchmark
question fixture. At least one tool in the list must fire for the question to pass.

### Synonym table lookup is case-insensitive (key.strip().lower())
Input is lowercased before lookup; trailing `.,;:!?` are stripped.

### WXO token refresh pattern (MUST use `--api-key` flag)
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
```

### XBRL derived-metric early-exit path
`sec_edgar_resolve_xbrl_concept`: when a query matches both `_CANONICAL` AND `_DERIVED_HINTS`,
the early-exit path at the top of the function fires before the inverted-index search.
This is needed for acronyms like "ebitda" that have no index hits.
If you add new derived terms, add them to BOTH `_DERIVED_HINTS` AND `_CANONICAL`.

### FASB taxonomy source files are gitignored
`.bob/artifacts/us-gaap-2026/` — generated output `xbrl_concepts_data.py` IS committed.

### arize-phoenix upgraded to 21.0.0 — always use venv/bin/python
Never run `python create_dataset.py` — always use `venv/bin/python create_dataset.py`.

---

## Known remaining gaps / future work (session 16 candidates)

### High priority

1. **CE redeploy for session 15 server.py changes** (~20 min):
   The new XBRL ratio entries (ROE, D/E, P/E, asset turnover, BVPS) are in `server.py`
   but not yet live. Run CR quota cleanup first (commands above), then deploy, tag `v1.8.0`.

2. **Update docs** (~15 min):
   - `docs/submission.md`: update BQ count 37→38, assertion count 291→359, add BQ-38 note,
     add new XBRL ratio overrides section, add v1.8.0 milestone
   - `evaluation/interpretation.md`: same updates

3. **New Phoenix Experiment 19** (~1 hr):
   After CE redeploy, rebuild dataset and re-run:
   ```bash
   venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2
   source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
   venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml
   ```

### Medium priority

4. **Additional international ADR synonyms** (~20 min):
   Other frequently queried ADRs still missing:
   - Roche (`RHHBY`) — Roche Holding AG
   - AstraZeneca (`AZN`) — AstraZeneca PLC (already US-listed)
   - Nestlé (`NSRGY`) — Nestle S.A.
   - HDFC Bank (`HDB`) — HDFC Bank Ltd

5. **BQ-39 — ROE/D-E ratio derived chain** (~30 min):
   Add a benchmark question exercising the new ratio hint entries, e.g.:
   "What is Apple's return on equity for fiscal year 2026?" — expected tools:
   `sec_edgar_resolve_xbrl_concept` (returns ROE derivation_note) → `sec_edgar_get_company_fact` ×2.

---

## Recommended start for session 16

**Start with CE redeploy** (session 15 server changes are not live yet).
Run CR quota cleanup first, deploy, tag `v1.8.0`, smoke-test BQ-38 on the live CE endpoint.

Then update docs (`submission.md` + `interpretation.md`) to reflect 38 BQs / 359 assertions.

Optionally run Phoenix Experiment 19 for updated eval documentation.
