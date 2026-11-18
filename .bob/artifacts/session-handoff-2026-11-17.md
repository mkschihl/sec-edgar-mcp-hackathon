# SEC EDGAR Project — Session Handoff (2026-11-18)

Read this file first, then the files listed under "Key files to load" before doing any work.

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
| Phoenix server | Already running on this VM — pid check: `ss -tlnp \| grep 6006` — UI at http://localhost:6006 |
| Phoenix run command | `source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL && venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-0` |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` |
| Active branch | `fixes-round2` (not yet pushed / merged to main) |
| Last commit | `8f49e68` — "feat(eval): implement items A–E ✅" |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1 — 8-tool MCP server | ✅ Complete | Deployed to Code Engine, always warm |
| M2 — Toolkit re-imported as remote HTTP | ✅ Complete | `sec_edgar_tools` using streamable_http in WXO |
| M3 — Evaluation harness | ✅ Complete | Phoenix run complete — 17/20 correctness, 20/20 scope (eval-0) |
| M4 — Eval code improvements (items A–E) | ✅ Complete | All eval code updated; `sec-edgar-eval-1` dataset created (23 Qs) |

---

## Session summary: 2026-11-17 → 2026-11-18

**Trigger instruction:**
> "Please update the evaluation code. Do not run experiments yet. Show me the diffs.
> The venv uses arize-phoenix-evals 3.9.5 and arize-phoenix-client 3.7.0."

All five items (A–E) were implemented and committed in `8f49e68`. No experiments were run.

### Item A — Judge `_INPUT_MAPPING` fix

**Root cause:** Phoenix `create_evaluator` decorator auto-binds named params (`input`, `output`, `reference`, `metadata`) from the experiment context; the old `_INPUT_MAPPING` class approach was broken in arize-phoenix-client 3.7.0.

**`eval/phoenix/judges/correctness_judge.py`:**
- Wrapped `ClassificationEvaluator` in `@create_evaluator(name="correctness")` with signature `(input, output, reference)`
- Added 3 grading rules: N-item shortfall, raw dates OK for fiscal years, comparability warnings advisory
- Emits a warning at import time when `JUDGE_MODEL == AGENT_MODEL`

**`eval/phoenix/judges/relevance_judge.py`:**
- Same `@create_evaluator(name="relevance")` wrapper pattern with `(input, output)`

**Correct import path (confirmed working in this venv):**
```python
from phoenix.client.resources.experiments import create_evaluator
```

### Item B — New `eval/phoenix/judges/numeric_judge.py`

- `check_numeric_accuracy()` evaluator with `metadata.numeric_checks` support
- Short-circuits to `numeric_pass` (no LLM call) when no checks defined for a question
- Wired into `run_experiment.py` alongside the existing two judges
- Exported from `judges/__init__.py`

### Item C — `eval/phoenix/agent.py` improvements

- `system_prompt_version="yaml"` reads `instructions:` from `agents/sec_edgar_agent.yaml`
- `_load_yaml_prompt()` tries `data.get("instructions")` first, then `data.get("spec", {}).get("instructions", "")` as fallback
- `_class_instrumented: bool = False` **class variable** (not instance variable) prevents double-instrumentation across the per-task fresh-instance loop
- `agent.close()` called in `finally` block of `create_experiment_task()`
- `recursion_limit: 15` passed via `config=` to `ainvoke`
- `PROMPT_VERSIONS = ["v1", "v2", "yaml"]` added to `run_experiment.py`

### Item D — `evaluation/run_evaluation.py` improvements

- `load_token()`: expired token → `sys.exit(1)` (was WARNING + continue)
- `call_agent_rest()`: timeout 60s→120s; captures `sse_events` list and `call_counts` dict; tool names from `step_details` **only** (no text scanning)
- `extract_tools_fired()`: uses `raw["tool_calls"]` key directly
- Removed `"i would need"` from `REFUSAL_PATTERNS`
- `score_question()`: `out_of_scope` category inverted logic; `<40 char` response → `partial`
- `generate_report()`: "Total Calls" column in Tool Utilisation table
- `main()`: `evaluation/traces/` dir auto-created; per-question `BQ-NN.json` trace saved; `call_counts` + `sse_events` in result dict; inline call count display

**SSE tool_calls location (key discovery):**
Tool names come from `delta.get("step_details", {}).get("tool_calls", [])` in the WXO SSE stream. Text-scanning was unreliable — only `"tool_calls"` key in the raw dict is used now.

### Item E — 23-question benchmark + `sec-edgar-eval-1` dataset

- `evaluation/benchmark_questions.py`: `numeric_checks` on BQ-07/09/14/17/20; `None` on all others; refined `pass_criteria` on 8 questions; BQ-21 (stock price), BQ-22 (investment advice), BQ-23 (revenue forecast) added as `out_of_scope` category
- `eval/phoenix/build_dataset.py` (new): CLI that builds `sec-edgar-eval-1.csv` from `benchmark_questions.py`; dry-run validated ✅
- `eval/phoenix/datasets/sec-edgar-eval-1/examples/sec-edgar-eval-1.csv` created (23 rows, columns: `query`, `responses`, `metadata`)
- `eval/phoenix/datasets.yaml`: `sec-edgar-eval-1` entry with `metadata_keys: [metadata]`
- `eval/phoenix/create_dataset.py`: reads and passes `metadata_keys`; validates metadata columns in CSV; both datasets dry-run validated ✅

---

## Git log (last 8 commits)

```
8f49e68  feat(eval): implement items A–E ✅
ad60c73  chore: add mcp-eval-wxai skill and watsonx.ai SDK smoke test script
bed52ba  fix(eval): fix phoenix_otlp_endpoint kwarg and env var validation for watsonx.ai
84471e1  fix(eval): update phoenix.client API calls for arize-phoenix v21
2751cee  feat(eval): migrate Phoenix harness from USAI gateway to watsonx.ai
b299ae8  chore: add IBMCLOUD_API_KEY and WXO_API_KEY to .env.example
a45b8e9  feat(agent): add 3 starter prompts for quarterly EPS, debt concepts, company identity
e041795  fix(server): deduplicate FY observations in sec_edgar_get_company_fact
```

---

## Next steps (recommended order)

### 1. Push `fixes-round2` to remote
```bash
cd /home/itzuser/wxo-agentic-workflow
git push origin fixes-round2
```

### 2. Run the Phoenix experiment against `sec-edgar-eval-1`
Get baseline scores with the numeric judge and all 23 questions:
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
venv/bin/python eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-1
```

### 3. Run `--system-prompt-version yaml` A/B comparison
```bash
venv/bin/python eval/phoenix/run_experiment.py \
  --dataset-name sec-edgar-eval-1 \
  --system-prompt-version yaml
```
Compare in Phoenix UI: Datasets → `sec-edgar-eval-1` → Compare experiments.

### 4. Inspect any incorrect responses in Phoenix
Open http://localhost:6006, go to the `sec-edgar-eval-1` dataset → Experiments → look at questions where `correctness = incorrect`. Determine root cause:
- **Tool schema issue** → fix in `toolkits/sec_edgar_tools/server.py`, redeploy to Code Engine
- **Agent instruction gap** → fix in `agents/sec_edgar_agent.yaml`, re-import with `orchestrate agents import`
- **Judge too strict** → adjust prompt template in `eval/phoenix/judges/correctness_judge.py`

### 5. Update `docs/submission.md` with final eval scores
Replace placeholder scores with actual `sec-edgar-eval-1` results (correctness + numeric accuracy).

### 6. Merge `fixes-round2` to `main`
```bash
git checkout main && git merge fixes-round2 && git push origin main
```

---

## Key files

```
agents/sec_edgar_agent.yaml                              ← live agent (top-level instructions: key)
toolkits/sec_edgar_tools/server.py                       ← deployed to Code Engine (8 tools, all fixes)
eval/phoenix/agent.py                                    ← updated: yaml prompt, _class_instrumented, close, recursion_limit
eval/phoenix/run_experiment.py                           ← updated: numeric_judge wired, PROMPT_VERSIONS += "yaml"
eval/phoenix/build_dataset.py                            ← NEW: generates sec-edgar-eval-1.csv
eval/phoenix/datasets.yaml                               ← updated: sec-edgar-eval-1 with metadata_keys
eval/phoenix/create_dataset.py                           ← updated: metadata_keys + validation
eval/phoenix/judges/__init__.py                          ← updated: exports check_numeric_accuracy
eval/phoenix/judges/correctness_judge.py                 ← updated: @create_evaluator wrapper, 3 rules, model warning
eval/phoenix/judges/relevance_judge.py                   ← updated: @create_evaluator wrapper
eval/phoenix/judges/numeric_judge.py                     ← NEW: check_numeric_accuracy() with numeric_checks
eval/phoenix/datasets/sec-edgar-eval-1/examples/         ← NEW: 23-row CSV
eval/phoenix/prompts/system_prompt_v1.txt                ← unchanged
eval/phoenix/prompts/system_prompt_v2.txt                ← unchanged
evaluation/run_evaluation.py                             ← updated: SSE fixes, scoring, traces, timeout
evaluation/benchmark_questions.py                        ← updated: 23 Qs, numeric_checks, out_of_scope BQ-21/22/23
evaluation/raw_results.json                              ← output from last run_evaluation.py run
evaluation/EVAL_REPORT.md                                ← output from last run_evaluation.py run
evaluation/traces/                                       ← DOES NOT EXIST YET (auto-created on first run)
docs/demo_walkthrough.md                                 ← 8-step hackathon demo script
docs/submission.md                                       ← hackathon submission write-up
```

---

## Skills to activate

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns (`.bob/skills/mcp-eval-wxai/SKILL.md`)
