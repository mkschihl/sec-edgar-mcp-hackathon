# SEC EDGAR Project — Session Handoff (2026-11-23, end of session 13+deploy)

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
| watsonx.ai URL | `https://ca-tor.ml.cloud.ibm.com` |
| watsonx.ai project ID | `2d244f0a-a04f-4585-b4eb-94da0b59541a` |
| Phoenix server | Running on this VM — UI at http://localhost:6006 — check: `ss -tlnp \| grep 6006` |
| Phoenix run command | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL && venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml` |
| Run evaluator (no Phoenix) | `source .env && export WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID && venv/bin/python evaluation/run_evaluation.py` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` |
| Active branch | `main` at `58e9d9c` |
| Last commit | `1cfc4f3` — "chore: session handoff 2026-11-23 (session 13 complete — ADR synonyms, 274 assertions, BQ-36, 36/36, v1.5.0)" |
| WXO instance ID | `76b76ce7-8b9e-4f7e-885b-967fbaef80c9` |
| WXO agent ID | `dd7fadae-34b2-478b-98c4-2fc48cbd35e5` (sec_edgar_agent) |
| Re-import toolkit | `venv/bin/orchestrate toolkits add --kind mcp --name sec_edgar_tools --description "SEC EDGAR toolkit: company lookup, filing history, and XBRL financial-statement facts from the SEC's public APIs." --url "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp" --transport streamable_http --tools "*"` |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |
| Active model vars | `AGENT_MODEL=meta-llama/llama-3-3-70b-instruct` / `JUDGE_MODEL=mistralai/mistral-small-3-1-24b-instruct-2503` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1–M37 | ✅ Complete | See session-12 handoff for details |
| M38 — ADR synonym additions (TSMC/SAP/ASML/Sony) | ✅ Complete | 13 new entries, 274 assertions; commit `f834a9a` |
| M39 — BQ-36 chain eval (xbrl_concept → compare_companies) | ✅ Complete | 36/36 pass; commit `58e9d9c`; tagged `v1.5.0` |
| M40 — CE redeploy for session 13 synonym changes | ✅ Complete | Build run `sec-edgar-tools-mks-run-261123-073757546`; smoke-tested BQ-32/BQ-33 ✅ |

---

## This session's changes (session 13)

### Commits

```
58e9d9c  feat(eval): add BQ-36 xbrl_concept_chain (resolve→compare deferred revenue); 36/36 pass (100%)  ← HEAD
f834a9a  feat(server): add international ADR synonyms (TSMC/TSM, SAP SE, ASML, Sony); 274 assertions
1555677  chore: session handoff 2026-11-23 (session 12 complete — 35/35 eval, 73 XBRL overrides, Exp 17)
```

Tags: `v1.5.0` → `58e9d9c`

### What changed in session 13

1. **International ADR synonym additions** (`f834a9a`):
   - **TSMC/Taiwan Semiconductor**: 3 new entries — `taiwan semiconductor`, `taiwan semiconductor manufacturing`, `tsm`
     (all → "Taiwan Semiconductor Manufacturing Co" / TSM)
   - **SAP SE**: 1 new entry — `sap se` (joins existing `sap`)
   - **ASML**: 2 new entries — `asml`, `asml holding`
     (→ "ASML Holding N.V." / ASML)
   - **Sony**: 3 new entries — `sony`, `sony group`, `sony corp`
     (→ "Sony Group Corp" / SONY; note: Sony Corp → Sony Group Corp rebrand 2021)
   - **Toyota ADR aliases**: 2 new entries — `toyota motor`, `tm`
     (joins existing `toyota`; `tm` = ADR ticker)
   - Total synonym table: 175 → ~186 entries (≈11 net new keys + minor note text updates)
   - Existing `tsmc`/`sap`/`toyota` entries: note text updated to include "(ADR: TSM/SAP/TM)" context

2. **Test 16 expansion** (`f834a9a`):
   - 18 new assertions covering all 5 ADR companies
   - Total assertions: 256 → **274, all passing**
   - New assertions cover: canonical_name, ticker, lowercase/mixed case, alternate name forms

3. **BQ-36 chain benchmark question** (`58e9d9c`):
   - New category 18: `xbrl_concept_chain`, difficulty `hard`
   - Question: "Compare deferred revenue across Apple, Microsoft, and Alphabet for the most recent fiscal year. Which company had the highest deferred revenue?"
   - Expected tools: `sec_edgar_resolve_xbrl_concept` → `sec_edgar_compare_companies`
   - Actual trace: agent additionally called `sec_edgar_search_companies` ×3 (to resolve tickers to CIKs) + `sec_edgar_compare_companies` ×2
   - **PASS on first run** — agent correctly resolved concept, compared all three companies, named Microsoft as highest
   - `evaluation/benchmark_questions.py`: category mapping updated (categories 14–18 documented)
   - `eval/phoenix/build_dataset.py`: BQ-36 reference answer added
   - Phoenix CSV: 35 rows → **36 rows**

4. **v1.5.0 tagged and pushed**:
   - Tag: `git tag -a v1.5.0 -m "v1.5.0: ADR synonyms (TSMC/SAP/ASML/Sony), 274 regression assertions, BQ-36 chain eval (36/36)"`
   - Pushed to `github.com:mkschihl/wxo-agentic-workflow.git`

---

## Current evaluation state (canonical — `run_evaluation.py`)

**36/36 pass (100%)** — last run 2026-11-23, commit `58e9d9c`.

---

## Git log (last 10 commits)

```
58e9d9c  feat(eval): add BQ-36 xbrl_concept_chain (resolve→compare deferred revenue); 36/36 pass (100%)  ← HEAD, main, v1.5.0
f834a9a  feat(server): add international ADR synonyms (TSMC/TSM, SAP SE, ASML, Sony); 274 assertions
1555677  chore: session handoff 2026-11-23 (session 12 complete — 35/35 eval, 73 XBRL overrides, Exp 17)
db927d2  feat(server): expand XBRL canonical overrides 40→73; add test_xbrl_concept_resolver (256 assertions)
0c014d6  docs(eval): add Phoenix Experiment 17 results (35 Qs, Llama-agent)
41fd17b  chore(eval): rebuild Phoenix CSV to 35 rows (BQ-34/35 added)
04c223b  fix(eval): accept alternate routing paths for BQ-01/02/15; 35/35 pass (100%)
55b1a8d  docs(eval): update to 35 BQs/14 tools; BQ-34/35 pass 2026-11-23
44758ca  fix(agent): update instructions to fourteen tools
ffee5f4  fix(server): update FastMCP instructions to fourteen tools, add resolve_xbrl_concept entry
```

Tags: `v1.0.0` → `e604b36`, `v1.1.0` → `752e86d`, `v1.2.0` → `ed168e7`, `v1.3.0` → `0ebb2dd`, `v1.4.0` → `55b1a8d`, **`v1.5.0` → `58e9d9c`**

---

## Key files

```
agents/sec_edgar_agent.yaml              ← 14 tools; Rules 0–13; "fourteen tools" in instructions
                                           Current in WXO (re-imported session 12)

toolkits/sec_edgar_tools/server.py       ← 14 tools; _CANONICAL has 73 entries; ~186 synonym entries
toolkits/sec_edgar_tools/xbrl_concepts_data.py  ← 7,462 FASB US-GAAP 2026 concepts (generated)
toolkits/sec_edgar_tools/Dockerfile      ← COPY includes xbrl_concepts_data.py (fixed session 12)
toolkits/sec_edgar_tools/test_regressions.py    ← 21 test functions, 274 assertions; all pass

evaluation/run_evaluation.py             ← supports any_of_tools field
evaluation/benchmark_questions.py        ← 36 Qs; 18 categories; BQ-36 = xbrl_concept_chain
evaluation/raw_results.json              ← 36 results (36/36 pass, run 2026-11-23)
evaluation/EVAL_REPORT.md                ← 36/36 pass, run 2026-11-23

eval/phoenix/build_dataset.py            ← _REFERENCE_ANSWERS for BQ-01–BQ-36
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← 36 rows

docs/submission.md                       ← updated through session 12 (35 BQs, 14 tools, Exp 17)
evaluation/interpretation.md             ← updated through session 12
```

**Note**: `docs/submission.md` and `evaluation/interpretation.md` were NOT updated this session —
they still reference 35 BQs and Experiment 17. They should be updated in session 14 if submission docs matter.

---

## CE deploy status

**✅ Deployed end of session 13.** Build run `sec-edgar-tools-mks-run-261123-073757546` completed
successfully. All new synonym entries (TSMC aliases, SAP SE, ASML, Sony, Toyota ADR aliases) are
live on the CE container. Smoke-tested via eval runner: BQ-32 ✅ BQ-33 ✅.

The server is fully current at HEAD `1cfc4f3`. No CE deploy is needed at the start of session 14.

---

## Discoveries (critical for new sessions)

### Dockerfile must list all Python files explicitly
`COPY server.py app.py xbrl_concepts_data.py ./` — if a new Python module is added to the
toolkit, it MUST be added to this COPY line or the container will crash on import.

### any_of_tools scoring field
`evaluation/run_evaluation.py` supports `any_of_tools: [t1, t2]` in a benchmark
question fixture. At least one tool in the list must fire for the question to pass.
Used for BQ-02 where the agent non-deterministically routes via either
`sec_edgar_resolve_synonym` or `sec_edgar_search_companies`.

### Synonym table lookup is case-insensitive (key.strip().lower())
Input is lowercased before lookup; trailing `.,;:!?` are stripped.
Test entries should use mixed-case input (e.g. "TSMC", "Sony") to verify the lowercasing.

### WXO token refresh pattern (MUST use `--api-key` flag)
```bash
source .env && export WXO_API_KEY
venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"
```

### score_wxo_results.py uses _REFERENCE_ANSWERS (session 10 change)
When adding a new BQ, add both: (1) `pass_criteria` in `benchmark_questions.py` and
(2) a `_REFERENCE_ANSWERS` entry in `eval/phoenix/build_dataset.py`.

### FASB taxonomy source files are gitignored
`.bob/artifacts/us-gaap-2026/` — generated output `xbrl_concepts_data.py` IS committed.

### arize-phoenix upgraded to 21.0.0 — always use venv/bin/python
Never run `python create_dataset.py` — always use `venv/bin/python create_dataset.py`.

---

## Known remaining gaps / future work (session 14 candidates)

### High priority

1. **sec_edgar_compare_companies 3rd BQ (BQ-37)** (~20 min):
   Only 2 BQs (BQ-13, BQ-14) for a complex tool. A 4+ company comparison or
   multi-year trend would stress-test it. Add BQ-37 (category 7 / cross_company_comparison).

2. **docs/submission.md + interpretation.md update** (~20 min):
   Both files still reference 35 BQs, 14 tools, Experiment 17. Update to reflect
   36 BQs, v1.5.0 tag, and session 13 synonym additions.

### Medium priority

3. **Phoenix Experiment 18** (~1 hr):
   Re-run the Phoenix eval experiment (Exp 17 was at 35 Qs). CSV is now 36 rows.
   Run:
   ```bash
   source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
   venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml
   ```

4. **Additional XBRL canonical override additions** (15 min):
   The 73-entry table still has gaps. Useful additions:
   - `net debt` → `LongTermDebt` + offset note (not a single concept)
   - `working capital` → `AssetsCurrent` / `LiabilitiesCurrent` (derived, not a concept)
   - `ebitda` → no single GAAP concept (derived) — return a hint explaining derivation
   - `minority interest` → `MinorityInterest` (deprecated) / `NoncontrollingInterestMember`
   - `other comprehensive income` → `OtherComprehensiveIncomeLossNetOfTax`

5. **Additional international ADR synonyms** (~30 min):
   Other frequently queried ADRs still missing from the synonym table:
   - Alibaba (`BABA`) — Alibaba Group Holding Ltd
   - LVMH (`LVMUY`) — LVMH Moët Hennessy Louis Vuitton SE
   - Novo Nordisk (`NVO`) — Novo Nordisk A/S
   - Shell plc already present (`SHEL`) ✓
   - Rio Tinto (`RIO`) — Rio Tinto plc

---

## Recommended start for session 14

**No CE deploy needed** — server is fully current at HEAD `1cfc4f3`, deployed and smoke-tested end of session 13.

**Start with BQ-37** (item 1 above, ~20 min) — a 4-company `compare_companies` stress test.
Then update **docs/submission.md + interpretation.md** (item 2, ~20 min) to reflect 36 BQs and v1.5.0.

Both together are ~40 min and leave the project fully documented.

---

## Skills to activate in a fresh session

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns
