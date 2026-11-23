# SEC EDGAR Project — Session Handoff (2026-11-23, end of session 14)

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
| Active branch | `main` at `5178931` |
| Last commit | `5178931` — "feat(server): add XBRL derived-metric hints and new ADR synonyms; 291 regression assertions" |
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
| M40 — CE redeploy for session 13 synonym changes | ✅ Complete | Build run `sec-edgar-tools-mks-run-261123-073757546` |
| M41 — BQ-37 4-company compare_companies stress test | ✅ Complete | 37/37 pass; commit `c0cf335`; tagged `v1.6.0` |
| M42 — Docs updated to 37 BQs, v1.6.0 | ✅ Complete | `docs/submission.md` + `evaluation/interpretation.md`; commit `b19c544` |
| M43 — Phoenix Experiment 18 (37 Qs) | ✅ Complete | 37/37 task runs, 111 evals; Exp ID `RXhwZXJpbWVudDoxOQ==`; commit `b19c544` |
| M44 — XBRL derived-metric hints (net debt/working capital/EBITDA/minority interest/OCI) | ✅ Complete | 5 new `_CANONICAL` entries, 3 `_DERIVED_HINTS`; early-exit path for acronyms |
| M45 — ADR synonyms (Alibaba/LVMH/Novo Nordisk/Rio Tinto) | ✅ Complete | 12 new entries; 198 total synonym entries |
| M46 — Regression assertions 274 → 291 | ✅ Complete | All passing |
| M47 — CE redeploy for session 14 server.py changes | ✅ Complete | Build run `sec-edgar-tools-mks-run-261123-162644082`; tagged `v1.7.0` |

---

## This session's changes (session 14)

### Commits

```
5178931  feat(server): add XBRL derived-metric hints and new ADR synonyms; 291 regression assertions  ← HEAD, v1.7.0
b19c544  docs: update submission.md and interpretation.md to 37 BQs, v1.6.0, Exp 18
```

Tags: `v1.7.0` → `5178931`

### What changed in session 14

1. **Docs updated to 37 BQs + Exp 18** (`b19c544`):
   - `docs/submission.md`: 35→37 BQs throughout, tool utilisation table updated,
     production scoring section updated, Milestones M9/M10 added, synonym ~186, 274 assertions,
     Exp 17 note updated, Exp 18 results added
   - `evaluation/interpretation.md`: same updates + BQ-36/BQ-37 notes, eval method
     change log extended, Exp 18 row in table, `(Exp 18 pending)` marker replaced with results

2. **Phoenix Experiment 18** (`b19c544`):
   - Dataset rebuilt to 37 rows and re-uploaded to Phoenix before run
   - 37/37 task runs completed, 111 evaluations
   - Exp ID: `RXhwZXJpbWVudDoxOQ==` (Phoenix internal numbering: Exp 19)
   - Scores: correctness 14/37 (38%), scope 30/37 (81%), numeric 5/8 (62%)
   - Consistent with Exp 17 (35 Qs); Llama standalone model, not production WXO

3. **XBRL derived-metric hints** (`5178931`):
   - `_DERIVED_HINTS` dict (3 entries) with formula notes for `net debt`, `working capital`, `ebitda`
   - Early-exit path before the inverted-index search handles acronyms (like "ebitda")
     that have no index hits but do have canonical overrides
   - `_CANONICAL` table: 73 → 80 entries, 7 new additions:
     - `net debt` → LongTermDebt + ShortTermBorrowings + DebtCurrent + Cash (+ derivation_note)
     - `working capital` → AssetsCurrent + LiabilitiesCurrent (+ derivation_note)
     - `ebitda` → OperatingIncomeLoss + DepreciationAndAmortization (+ derivation_note)
     - `minority interest` / `noncontrolling interest` / `non-controlling interest` → MinorityInterest
     - `other comprehensive income` / `oci` → OtherComprehensiveIncomeLossNetOfTax
     - `aoci` / `accumulated other comprehensive income` → AccumulatedOtherComprehensiveIncomeLossNetOfTax

4. **ADR synonym additions** (`5178931`):
   - 12 new entries in `_SYNONYM_TABLE` (198 total):
     - Alibaba / alibaba group / BABA → Alibaba Group Holding Ltd (BABA)
     - LVMH / louis vuitton / moet hennessy / LVMUY → LVMH Moet Hennessy Louis Vuitton SE (LVMUY)
     - novo nordisk / NVO → Novo Nordisk A/S (NVO)
     - rio tinto / RIO → Rio Tinto PLC (RIO)
   - Regression test assertions: 274 → **291**, all passing

5. **CE redeploy + CR quota management**:
   - Container Registry was over-quota (540 MB / 512 MB limit)
   - Fix: `ibmcloud cr image-prune-untagged --restrict gsa-hackathon-cr-student7 --force`
     then restore+delete all 31 trashed digests via loop
   - Quota dropped to 70 MB; deploy succeeded
   - **Future sessions**: always run the quota cleanup before deploying

---

## Current evaluation state (canonical — `run_evaluation.py`)

**37/37 pass (100%)** — last run 2026-11-23, commit `5178931`.

---

## Git log (last 8 commits)

```
5178931  feat(server): add XBRL derived-metric hints and new ADR synonyms; 291 regression assertions  ← HEAD, main, v1.7.0
b19c544  docs: update submission.md and interpretation.md to 37 BQs, v1.6.0, Exp 18
ef820ce  chore: update s13 handoff — M41 BQ-37 complete, 37/37, v1.6.0, session 14 start updated
c0cf335  feat(eval): add BQ-37 4-company compare_companies stress test; 37/37 pass (100%)  v1.6.0
f572684  chore: update s13 handoff — CE deploy done, M40 complete
1cfc4f3  chore: session handoff 2026-11-23 (session 13 complete)
58e9d9c  feat(eval): add BQ-36 xbrl_concept_chain (resolve→compare deferred revenue)  v1.5.0
f834a9a  feat(server): add international ADR synonyms (TSMC/TSM, SAP SE, ASML, Sony); 274 assertions
```

Tags: `v1.0.0`–`v1.4.0` (earlier), `v1.5.0` → `58e9d9c`, `v1.6.0` → `c0cf335`, **`v1.7.0` → `5178931`**

---

## Key files

```
agents/sec_edgar_agent.yaml              ← 14 tools; Rules 0–13; "fourteen tools" in instructions
                                           Current in WXO (re-imported session 12)

toolkits/sec_edgar_tools/server.py       ← 14 tools; _SYNONYM_TABLE 198 entries; _CANONICAL 80 entries;
                                           _DERIVED_HINTS 3 entries; early-exit path for derived metrics
toolkits/sec_edgar_tools/xbrl_concepts_data.py  ← 7,462 FASB US-GAAP 2026 concepts (generated)
toolkits/sec_edgar_tools/Dockerfile      ← COPY includes xbrl_concepts_data.py
toolkits/sec_edgar_tools/test_regressions.py    ← 21 test functions, 291 assertions; all pass

evaluation/run_evaluation.py             ← supports any_of_tools field
evaluation/benchmark_questions.py        ← 37 Qs; 18 categories; BQ-36 = xbrl_concept_chain, BQ-37 = compare ×4
evaluation/raw_results.json              ← 37 results (37/37 pass, run 2026-11-23)
evaluation/EVAL_REPORT.md                ← 37/37 pass, run 2026-11-23

eval/phoenix/build_dataset.py            ← _REFERENCE_ANSWERS for BQ-01–BQ-37
eval/phoenix/datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv  ← 37 rows

docs/submission.md                       ← updated through session 14 (37 BQs, v1.7.0, Exp 18)
evaluation/interpretation.md             ← updated through session 14 (37 BQs, Exp 18)
```

---

## CE deploy status

**✅ Deployed end of session 14.** Build run `sec-edgar-tools-mks-run-261123-162644082` completed
successfully. All new XBRL hints and ADR synonyms (Alibaba, LVMH, Novo Nordisk, Rio Tinto) are
live on the CE container. Smoke-tested BQ-32 ✅ BQ-33 ✅.

**⚠️ Container Registry quota note**: The CR quota (512 MB / `us-south`) fills up quickly from
CE build runs. Before each new CE deploy, run:
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

---

## Discoveries (critical for new sessions)

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

### score_wxo_results.py uses _REFERENCE_ANSWERS (session 10 change)
When adding a new BQ, add both: (1) `pass_criteria` in `benchmark_questions.py` and
(2) a `_REFERENCE_ANSWERS` entry in `eval/phoenix/build_dataset.py`.
Then re-upload the dataset: `venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2`

### Phoenix dataset must be re-uploaded before each experiment run
The Phoenix server stores versioned snapshots. After adding BQs to the CSV, always run
`create_dataset.py` before `run_experiment.py` or the experiment will use the stale version.

### FASB taxonomy source files are gitignored
`.bob/artifacts/us-gaap-2026/` — generated output `xbrl_concepts_data.py` IS committed.

### arize-phoenix upgraded to 21.0.0 — always use venv/bin/python
Never run `python create_dataset.py` — always use `venv/bin/python create_dataset.py`.

### XBRL derived-metric early-exit path
`sec_edgar_resolve_xbrl_concept`: when a query matches both `_CANONICAL` AND `_DERIVED_HINTS`,
the early-exit path at the top of the function fires before the inverted-index search.
This is needed for acronyms like "ebitda" that have no index hits.
If you add new derived terms, add them to BOTH `_DERIVED_HINTS` AND `_CANONICAL`.

---

## Known remaining gaps / future work (session 15 candidates)

### Medium priority

1. **Additional XBRL canonical overrides** (~15 min):
   The 80-entry table still has gaps. Useful additions:
   - `book value per share` → `BookValuePerShare` or `StockholdersEquity` / `CommonStockSharesOutstanding`
   - `price to earnings` → no GAAP concept (derived) — return a hint
   - `return on equity` → `NetIncomeLoss` / `StockholdersEquity` (derived)
   - `asset turnover` → `Revenues` / `Assets` (derived)
   - `debt to equity` → `Liabilities` / `StockholdersEquity` (derived)

2. **Additional international ADR synonyms** (~20 min):
   Other frequently queried ADRs still missing:
   - Roche (`RHHBY`) — Roche Holding AG
   - AstraZeneca (`AZN`) — AstraZeneca PLC (already US-listed)
   - Nestlé (`NSRGY`) — Nestle S.A.
   - HDFC Bank (`HDB`) — HDFC Bank Ltd

3. **BQ-38 for XBRL derived-metric handling** (~30 min):
   Add a benchmark question that exercises the `derivation_note` path, e.g.:
   "What was Apple's EBITDA for fiscal year 2026?" — expected tools: `sec_edgar_resolve_xbrl_concept`
   (returns derivation_note + components) + `sec_edgar_get_company_fact` ×2

4. **New Phoenix Experiment 19** (~1 hr):
   After any BQ additions, rebuild dataset and re-run:
   ```bash
   venv/bin/python eval/phoenix/create_dataset.py --dataset-name sec-edgar-eval-2
   source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
   venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-2 --system-prompt-version yaml
   ```

---

## Recommended start for session 15

**No CE deploy needed** — server is fully current at HEAD `5178931`, deployed and smoke-tested
end of session 14.

**Start with BQ-38** (derived-metric benchmark question, ~30 min) if you want to add
measurement coverage for the new XBRL `derivation_note` feature.

Then optionally add remaining XBRL overrides or ADR synonyms (items 1–2 above) followed
by a CE redeploy (remember the CR quota cleanup first).

If a Phoenix experiment run is desired for final documentation, that's ~1 hr standalone.

---

## Skills to activate in a fresh session

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns
