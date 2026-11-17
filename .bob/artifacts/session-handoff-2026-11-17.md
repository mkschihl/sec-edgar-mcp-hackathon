# SEC EDGAR Project — Session Handoff (2026-11-17)

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
| WXO environment | `gsa-hackathon` — IBM Cloud Toronto (`ca-tor`) |
| WXO token refresh | `source .env && export WXO_API_KEY && venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |
| Code Engine project | `ce-550000w6t0` — resource group `eid-6ac40a21a8799c11a48dc107` |
| CE app URL | `https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp` |
| CE login | `ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r ca-tor -g Default` then `ibmcloud target -g eid-6ac40a21a8799c11a48dc107` then `ibmcloud ce project select --name ce-550000w6t0` |
| CE deploy command | `ibmcloud ce app update --name sec-edgar-tools-mks --build-source toolkits/sec_edgar_tools --build-dockerfile Dockerfile` |
| watsonx.ai URL | `https://ca-tor.ml.cloud.ibm.com` |
| watsonx.ai project ID | `2d244f0a-a04f-4585-b4eb-94da0b59541a` |
| Phoenix server | Already running on this VM — pid check: `ss -tlnp \| grep 6006` — UI at http://localhost:6006 |
| Git remote | `github.com:mkschihl/wxo-agentic-workflow.git` — branch `main` |
| .env setup | `source .env && export IBMCLOUD_API_KEY WXO_API_KEY WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL` |

---

## Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M1 — 8-tool MCP server | ✅ Complete | Deployed to Code Engine, always warm |
| M2 — Toolkit re-imported as remote HTTP | ✅ Complete | `sec_edgar_tools` using streamable_http in WXO |
| M3 — Evaluation harness | ✅ Complete | Phoenix run complete — 17/20 correctness, 20/20 scope |

---

## What was completed in this session (2026-11-14 → 2026-11-17)

### Option A — Demo walkthrough (`docs/demo_walkthrough.md`)
Scripted 8-step demo covering all tools in a logical progression.
Includes exact prompts, real example responses from the eval run, and
talking points for each step. Estimated demo time: 8–10 minutes.

### Option B — BQ-07 annual fact accuracy fix (`server.py`)
`sec_edgar_get_company_fact` now deduplicates FY observations by keeping
only the entry with the latest `filed` date per fiscal year end date.
This removes comparative-period restated values that were causing ~$1–3B
inaccuracies (e.g. FY2024 Apple net income was off by $3B).
**Deployed to Code Engine** (`e041795`).

### Option C — Hackathon submission write-up (`docs/submission.md`)
Full submission document: problem statement, Mermaid architecture diagram,
8-tool table, evaluation results (all 5 issues with resolution status),
key technical decisions, what Phoenix will add, and repo layout.

### Option D — Expanded starter prompts (`agents/sec_edgar_agent.yaml`)
Added 3 new starter prompts: quarterly EPS (`sp7`), debt concepts for a
company (`sp8`), company identity lookup (`sp9`). Agent re-deployed.

### Phoenix eval harness migrated to watsonx.ai
The harness previously used the USAI model gateway (OpenAI-compatible).
It now uses `ChatWatsonx` (agent) and `LLM(provider="litellm", model="watsonx/...")` 
(judges). All env vars updated from `USAI_*` to `WATSONX_*`.

### Phoenix experiment run completed (M3 fully done)
**Results — Experiment 1, prompt v1, `meta-llama/llama-3-3-70b-instruct`:**
- **Correctness: 17/20 = 85%** (3 marked incorrect by judge)
- **Scope: 20/20 = 100%** (agent never answered out-of-scope)

The 3 incorrect responses have not yet been inspected — that is the
recommended first task for the next session (see Next steps below).

---

## Git log (last 6 commits)

```
ad60c73  chore: add mcp-eval-wxai skill and watsonx.ai SDK smoke test script
bed52ba  fix(eval): fix phoenix_otlp_endpoint kwarg and env var validation for watsonx.ai
84471e1  fix(eval): update phoenix.client API calls for arize-phoenix v21
2751cee  feat(eval): migrate Phoenix harness from USAI gateway to watsonx.ai
b299ae8  chore: add IBMCLOUD_API_KEY and WXO_API_KEY to .env.example
a45b8e9  feat(agent): add 3 starter prompts for quarterly EPS, debt concepts, company identity
```

---

## Next steps (recommended order)

### 1. Inspect the 3 incorrect responses in Phoenix (no credentials needed)
Phoenix is already running on this VM. Open http://localhost:6006, go to
Datasets → `sec-edgar-eval-0` → Experiments → Experiment 2, and look at
the 3 questions where `correctness = incorrect`. Read the agent response
and the judge explanation to understand the root cause.

**To identify them from the CLI:**
```bash
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
# Query the GraphQL API for incorrect runs:
curl -s "http://localhost:6006/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ compareExperiments(baseExperimentId: \"RXhwZXJpbWVudDoy\", compareExperimentIds: []) { edges { node { example { input } repeatedRunGroups { runs { output { result } annotations { edges { node { name label score explanation } } } } } } } } }"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
for edge in d[\"data\"][\"compareExperiments\"][\"edges\"]:
    node = edge[\"node\"]
    for grp in node.get(\"repeatedRunGroups\",[]):
        for run in grp.get(\"runs\",[]):
            anns = run.get(\"annotations\",{}).get(\"edges\",[])
            for a in anns:
                ann = a[\"node\"]
                if ann.get(\"name\")==\"correctness\" and ann.get(\"label\")==\"incorrect\":
                    print(\"Q:\", node[\"example\"].get(\"input\",{}).get(\"query\",\"\"))
                    print(\"Response:\", run[\"output\"].get(\"result\",\"\")[:200])
                    print(\"Explanation:\", ann.get(\"explanation\",\"\")[:300])
                    print()
"
```

### 2. Run prompt v2 experiment (A/B comparison)
Run the scope-bounded prompt version to see if it improves correctness:
```bash
cd /home/itzuser/wxo-agentic-workflow
source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID AGENT_MODEL JUDGE_MODEL
venv/bin/python eval/phoenix/run_experiment.py \
  --dataset-name sec-edgar-eval-0 \
  --system-prompt-version v2
```
Then compare v1 vs v2 side-by-side in Phoenix UI: Datasets → sec-edgar-eval-0 → Compare experiments.

### 3. Fix the root causes found in step 1
Depending on what the 3 incorrect responses show:
- **Tool schema issue** → fix in `toolkits/sec_edgar_tools/server.py`, redeploy to Code Engine
- **Agent instruction gap** → fix in `agents/sec_edgar_agent.yaml`, re-import with `orchestrate agents import`
- **Judge too strict** → adjust prompt template in `eval/phoenix/judges/correctness_judge.py`

### 4. Update `docs/submission.md` with final eval scores
Replace the "pending USAI credentials" placeholder with the actual results:
- Correctness: 17/20 = 85% (prompt v1)
- Scope: 20/20 = 100%
- Add v2 results once that run completes

---

## Key files

```
agents/sec_edgar_agent.yaml              ← current agent (10 starter prompts)
toolkits/sec_edgar_tools/server.py       ← current server (8 tools, all fixes applied)
eval/phoenix/agent.py                    ← Phoenix agent (ChatWatsonx)
eval/phoenix/judges/correctness_judge.py ← correctness judge (litellm watsonx/)
eval/phoenix/judges/relevance_judge.py   ← scope judge (litellm watsonx/)
eval/phoenix/run_experiment.py           ← experiment runner CLI
docs/demo_walkthrough.md                 ← 8-step hackathon demo script
docs/submission.md                       ← hackathon submission write-up
evaluation/interpretation.md             ← human audit narrative
```

---

## Skills to activate

- `wxo-builder` — ADK/orchestrate CLI reference
- `mcp-eval-wxai` — Phoenix + watsonx.ai eval harness patterns (`.bob/skills/mcp-eval-wxai/SKILL.md`)
