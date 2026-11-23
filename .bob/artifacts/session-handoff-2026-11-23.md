# SEC EDGAR Project — Session Handoff (2026-11-23, end of session 11)

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
| arize-phoenix | 21.0.0 (upgraded from 3.9.5 — always use `venv/bin/python`, never system `python`) |
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
| Active branch | `main` at `1e93711` |
| Last commit | `1e93711` — "feat(server): add sec_edgar_resolve_xbrl_concept (14th tool, FASB US-GAAP 2026)" |
| WXO instance ID | `76b76ce7-8b9e-4f7e-885b-967fbaef80c9` |
| WXO agent ID | `dd7fadae-34b2-478b-98c4-2fc48cbd35e5` (sec_edgar_agent) |
| Re-import toolkit | `venv/bin/orchestrate toolkits remove --name sec_edgar_tools && venv/bin/orchestrate toolkits add --kind mcp --name sec_edgar_tools --description "SEC EDGAR toolkit: company lookup, filing history, and XBRL financial-statement facts from the SEC's public APIs." --url "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp" --transport streamable_http --tools "*"` |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |
| Active model vars | `AGENT_MODEL=meta-llama/llama-3-3-70b-instruct` / `JUDGE_MODEL=mistralai/mistral-small-3-1-24b-instruct-2503` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1–M27 | ✅ Complete | See session-10 handoff for details |
| M28 — Reference answer fixes + scorer wiring | ✅ Complete | BQ-29 threshold removed; scorer now uses _REFERENCE_ANSWERS; commit `7b8e604` |
| M29 — BQ-32/BQ-33 for sec_edgar_resolve_synonym | ✅ Complete | 33/33 pass (100%); commit `73751a9` |
| M30 — Doc updates + _fetch_submission TTL cache | ✅ Complete | 31→33 BQs in all docs; 24h TTL cache; commit `fbf3d09` |
| M31 — asyncio.get_event_loop() fix in agent.py | ✅ Complete | No more `RuntimeError: Event loop is closed` noise; commit `5f851cb` |
| M32 — Phoenix CSV 33 rows + Experiment 16 (33/33) | ✅ Complete | All 33 tasks completed; 99 evaluations run; Experiment 16 = `RXhwZXJpbWVudDoxNg==` |
| M33 — sec_edgar_resolve_xbrl_concept (14th tool) | ✅ Complete | 7,462 FASB US-GAAP 2026 concepts; in-process index; BQ-34/35 added; commit `1e93711` |

---

## This session's changes (session 11)

### Commits

```
1e93711  feat(server): add sec_edgar_resolve_xbrl_concept (14th tool, FASB US-GAAP 2026)  ← HEAD
5f851cb  fix(eval): replace deprecated asyncio.get_event_loop() with asyncio.run() in agent.py
fbf3d09  docs+perf: update to 33 BQs/33/33; add TTL cache for _fetch_submission
```

### What changed in session 11

1. **Doc pass** (`fbf3d09`):
   - `docs/submission.md` + `evaluation/interpretation.md`: 31 BQs → 33 BQs / 31/31 → 33/33
     throughout; `sec_edgar_resolve_synonym` row added to routing tables; M7 milestone added.
   - Commit ref updated from `b7c6e6a` → `73751a9` in both docs.

2. **`_fetch_submission` TTL cache** (`fbf3d09`):
   - Upgraded from plain unbounded dict to 24h TTL pattern matching `_FACTS_CACHE`.
   - `_SUBMISSION_CACHE: dict[str, tuple[dict, float]]`, `_SUBMISSION_CACHE_TTL_SECONDS = 86_400.0`.
   - Two inline comments updated to "Both use a 24h TTL cache".

3. **`asyncio.get_event_loop()` → `asyncio.run()`** (`5f851cb`):
   - `eval/phoenix/agent.py:87` — `_make_langchain_tool` sync wrapper.
   - Eliminates `RuntimeError: Event loop is closed` noise from httpx teardown in Phoenix runs.

4. **Phoenix Experiment 16** (not committed — live in Phoenix):
   - Dataset rebuilt to 33 rows (BQ-32/33 were missing from previous 31-row CSV).
   - Experiment 16 (`RXhwZXJpbWVudDoxNg==`): 33/33 tasks completed, 99 evaluations run, exit 0.
   - View: http://localhost:6006/datasets/RGF0YXNldDoz/compare?experimentId=RXhwZXJpbWVudDoxNg==

5. **`sec_edgar_resolve_xbrl_concept` — 14th tool** (`1e93711`):
   - `toolkits/sec_edgar_tools/xbrl_concepts_data.py`: 7,462 non-abstract numeric
     concepts from FASB US-GAAP 2026 taxonomy. Each row: `(name, label, periodType, balance, xbrlType)`.
     Deprecated concepts excluded. Generated by `build_xbrl_concepts.py`.
   - `toolkits/sec_edgar_tools/build_xbrl_concepts.py`: one-time parser script.
     Source taxonomy at `.bob/artifacts/us-gaap-2026/` (gitignored).
   - `server.py`: inverted index built at import time (zero network calls per search).
     AND/OR fallback, stop-word filtering, 40-entry canonical override table,
     exact-name fast path, income-stmt heuristic (prefers `duration` for
     revenue/income/expense keywords), length penalty for simpler names.
   - `agents/sec_edgar_agent.yaml`: Rule 13 added; tool in tools list.
   - `evaluation/benchmark_questions.py`: BQ-34 (easy) + BQ-35 (medium, Pfizer operating CF).
   - `evaluation/run_evaluation.py`: tool added to `ALL_TOOL_NAMES`.
   - `eval/phoenix/build_dataset.py`: `_REFERENCE_ANSWERS` for BQ-34/35.
   - `.gitignore`: `.bob/artifacts/us-gaap-*/` excluded.

---

## Current evaluation state (canonical — `run_evaluation.py`)

**NOT YET RUN for BQ-34/35.** The last canonical run was 33/33 on 2026-11-21.
The 14th tool (`sec_edgar_resolve_xbrl_concept`) and BQ-34/35 have been added
but the Code Engine deploy and WXO agent re-import have NOT been done yet.

**Before running the evaluator**, you must:
1. Deploy the new server to Code Engine (adds 14th tool).
2. Re-import the agent YAML (adds Rule 13 and the tool).
3. Run `evaluation/run_evaluation.py` for BQ-34/35.

The 33 existing BQs should still pass — the new tool is additive only.

---

## Git log (last 8 commits)

```
1e93711  feat(server): add sec_edgar_resolve_xbrl_concept (14th tool)  ← HEAD, main
5f851cb  fix(eval): asyncio.get_event_loop() → asyncio.run() in agent.py
fbf3d09  docs+perf: update to 33 BQs/33/33; _fetch_submission TTL cache
f4bc2a4  chore: update handoff — Phoenix CSV 33 rows, Experiment 15 started
bda3f1d  chore: session handoff 2026-11-21 (session 10 complete)
73751a9  feat(eval): add BQ-32/33 for resolve_synonym; 33/33 pass
7b8e604  fix(eval): tighten reference answers; wire scorer to _REFERENCE_ANSWERS
3d2eb4a  chore: session handoff 2026-11-21 (session 9 complete)
```

Tags: `v1.0.0` → `e604b36`, `v1.1.0` → `752e86d`, `v1.2.0` → `ed168e7`, `v1.3.0` → `0ebb2dd`

---

## Key files

```
agents/sec_edgar_agent.yaml              ← 14 tools; Rules 0–13; 12 starter prompts
                                           NEEDS re-import after CE deploy

toolkits/sec_edgar_tools/server.py       ← 14 tools; 246 regression assertions
toolkits/sec_edgar_tools/xbrl_concepts_data.py  ← 7,462 FASB US-GAAP 2026 concepts (generated)
toolkits/sec_edgar_tools/build_xbrl_concepts.py ← one-time parser (taxonomy source in .bob/artifacts/)
toolkits/sec_edgar_tools/test_regressions.py    ← 246 assertions (tests 0–20); all pass

eval/phoenix/agent.py                    ← asyncio.run() fix applied (session 11)
eval/phoenix/build_dataset.py            ← _REFERENCE_ANSWERS for BQ-01–BQ-35
eval/phoenix/score_wxo_results.py        ← uses _REFERENCE_ANSWERS (not pass_criteria)
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← 33 rows (BQ-32/33 added session 11)

evaluation/run_evaluation.py             ← ALL_TOOL_NAMES has all 14 tools
evaluation/benchmark_questions.py        ← 35 Qs, 17 categories, all 14 tools
evaluation/raw_results.json              ← 33 results (BQ-01→BQ-33, run 2026-11-21) — STALE for BQ-34/35
evaluation/EVAL_REPORT.md                ← 33/33 pass, run 2026-11-21 — STALE for BQ-34/35

docs/submission.md                       ← updated session 11 (33 BQs, commit fbf3d09)
evaluation/interpretation.md             ← updated session 11 (same)
```

---

## Discoveries (critical for new sessions)

### arize-phoenix upgraded to 21.0.0 — always use venv/bin/python
System Python (`/usr/bin/python`) has an older `phoenix` without `phoenix.client`.
Never run `python create_dataset.py` — always use `venv/bin/python create_dataset.py`
(or run from workspace root with `venv/bin/python eval/phoenix/create_dataset.py`).

### FASB taxonomy source files are gitignored
`.bob/artifacts/us-gaap-2026/` contains the 2026 FASB taxonomy ZIp contents.
The generated output `toolkits/sec_edgar_tools/xbrl_concepts_data.py` IS committed.
To regenerate (e.g. for a 2027 taxonomy):
```bash
venv/bin/python toolkits/sec_edgar_tools/build_xbrl_concepts.py \
    --lab .bob/artifacts/us-gaap-YYYY/elts/us-gaap-lab-YYYY.xml \
    --xsd .bob/artifacts/us-gaap-YYYY/elts/us-gaap-YYYY.xsd \
    --out toolkits/sec_edgar_tools/xbrl_concepts_data.py
```

### sec_edgar_resolve_xbrl_concept — no network calls
The tool builds an in-process inverted index from `XBRL_CONCEPTS` at import time.
All 7,462 concepts are searched in memory. No EDGAR HTTP call. Fast path for exact
concept name input. Canonical override table for 40 common financial metrics.

### score_wxo_results.py uses _REFERENCE_ANSWERS (session 10 change)
`_build_reference()` imports `_REFERENCE_ANSWERS` from `eval/phoenix/build_dataset.py`.
When adding a new BQ, add both: (1) `pass_criteria` in `benchmark_questions.py` and
(2) a `_REFERENCE_ANSWERS` entry in `build_dataset.py`.

### WXO token refresh pattern (MUST use `--api-key` flag)
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
```

### _edgar_get() — rate-limited HTTP wrapper
All outbound SEC calls go through `_edgar_get(url, **kwargs)`. Never call
`client.get(...)` directly for new EDGAR HTTP calls.

---

## Known remaining gaps / future work (session 12 candidates)

### High priority

1. **CE deploy + agent re-import + run BQ-34/35** (45 min):
   The 14th tool (`sec_edgar_resolve_xbrl_concept`) is committed but NOT deployed to
   Code Engine and NOT re-imported into WXO. This is the first task for session 12.
   ```bash
   # 1. Deploy
   source .env && export IBMCLOUD_API_KEY
   ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default
   ibmcloud target -g eid-6ac40a21a8799c11a48dc107
   ibmcloud ce project select --name ce-550000w6t0
   ibmcloud ce app update --name sec-edgar-tools-mks --build-source toolkits/sec_edgar_tools --build-dockerfile Dockerfile

   # 2. Re-import agent
   source .env && export WXO_API_KEY
   venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
   venv/bin/orchestrate agents import -f agents/sec_edgar_agent.yaml

   # 3. Smoke test BQ-34 manually in WXO chat:
   #    "What is the XBRL concept name for 'operating cash flow'?"

   # 4. Run evaluator
   source .env && export WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID
   venv/bin/python evaluation/run_evaluation.py
   ```

2. **Update docs to 35 BQs** (10 min):
   `docs/submission.md` and `evaluation/interpretation.md` still say 33 BQs.
   Update to 35 BQs / 35/35 after the evaluator confirms BQ-34/35 pass.
   Also add sec_edgar_resolve_xbrl_concept to the tool table in both docs.

### Medium priority

3. **Phoenix Experiment 17** (30 min + wait):
   After CE deploy, rebuild the Phoenix CSV to 35 rows and run a new experiment:
   ```bash
   cd eval/phoenix && ../../venv/bin/python build_dataset.py
   ../../venv/bin/python create_dataset.py --dataset-name sec-edgar-eval-2
   source ../../.env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
   ../../venv/bin/python run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml
   ```

4. **v1.4.0 tag** (5 min):
   Tag the current HEAD `1e93711` as `v1.4.0` once BQ-34/35 pass.
   ```bash
   git tag -a v1.4.0 -m "v1.4.0: 14 tools, 35 BQs, FASB US-GAAP 2026 XBRL concept resolver"
   git push origin v1.4.0
   ```

### Lower priority

5. **International ADR synonym additions** (1 hr):
   TSMC, SAP SE, ASML, Sony, Toyota ADR are the main gaps in the 175-entry synonym table.

6. **XBRL concept synonym tool — additional canonical overrides** (30 min):
   The canonical override table in `sec_edgar_resolve_xbrl_concept` currently has 40 entries.
   Common gaps to add: `deferred revenue`, `contract liabilities`, `net pension liability`,
   `warranty liability`, `restructuring charges`, `stock-based compensation expense`.

7. **Additional BQs** for underrepresented tools:
   - `sec_edgar_compare_companies`: only 2 BQs — could add a 3rd with 4+ companies
   - `sec_edgar_resolve_xbrl_concept` → `sec_edgar_compare_companies` chain: not yet tested

---

## Recommended start for session 12

**Start with item 1 (CE deploy + re-import + BQ-34/35 eval).**
This takes ~45 minutes (mostly waiting for the CE build) and brings the deployed
server, the WXO agent, and the eval report into sync with the committed code.
Item 2 (doc updates) is a quick follow-on once the eval confirms 35/35.

---

## Skills to activate in a fresh session

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns
