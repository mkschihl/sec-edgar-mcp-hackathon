# SEC EDGAR — Phoenix Evaluation Harness

LLM-as-judge evaluation harness for the `sec_edgar_agent` using
[Arize Phoenix](https://docs.arize.com/phoenix).

The harness connects **directly to the live Code Engine `/mcp` endpoint** over
streamable-HTTP transport — no subprocess, no local server required.

---

## Prerequisites

1. **Python venv** with eval dependencies installed (see below).
2. **`.env` file** at the repo root — copy from `.env.example` and fill in:
   - `USAI_API_KEY` — API key for the GSA hackathon USAI model gateway
   - `USAI_BASE_URL` — Gateway base URL (e.g. `https://usai.example.gov`)
   - These come from the **hackathon lab portal / welcome email**, not from your
     watsonx Orchestrate instance. They are a separate OpenAI-compatible LiteLLM
     proxy. Do **not** put your WXO instance URL here.
3. **Phoenix server running locally** (`python -m phoenix.server.main serve`, UI at `:6006`).

> **Waiting for credentials?** The harness is fully built. Once you have USAI
> credentials, fill in `.env` and skip straight to step 5 of the Quick start.

---

## Quick start

```bash
# From the repo root — install pinned eval deps into the existing venv
venv/bin/python -m pip install -r requirements-eval.txt

# Start Phoenix
python -m phoenix.server.main serve &
# or: arize-phoenix serve

# Switch to the harness directory
cd eval/phoenix

# 1. Validate the dataset CSV (no upload)
python create_dataset.py --dataset-name sec-edgar-eval-0 --dry-run

# 2. Upload the dataset to Phoenix (one-time)
python create_dataset.py --dataset-name sec-edgar-eval-0

# 3. Run an experiment with the default v1 prompt
python run_experiment.py --dataset-name sec-edgar-eval-0

# 4. Run with the scoped v2 prompt for comparison
python run_experiment.py --dataset-name sec-edgar-eval-0 --system-prompt-version v2

# 5. Open Phoenix UI to review per-question traces and scores
open http://localhost:6006
```

---

## MCP endpoint

The agent connects to:

```
https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp
```

This is the always-warm IBM Code Engine deployment. Override with the `MCP_ENDPOINT`
env var if the URL changes.

---

## Directory structure

```
eval/phoenix/
├── agent.py                   # SECEdgarAgent (remote streamable-HTTP MCP transport)
├── create_dataset.py          # CLI: upload/validate a CSV dataset to Phoenix
├── run_experiment.py          # CLI: run agent + judges against a Phoenix dataset
├── datasets.yaml              # Dataset registry
├── README.md                  # This file
├── judges/
│   ├── __init__.py
│   ├── correctness_judge.py   # match_expected_response (vs ground truth)
│   └── relevance_judge.py     # check_answer_scope (in-scope / out-of-scope)
├── prompts/
│   ├── system_prompt_v1.txt   # Basic analyst prompt
│   └── system_prompt_v2.txt   # + explicit scope boundaries
└── datasets/
    └── sec-edgar-eval-0/
        └── examples/
            └── sec-edgar-eval-0.csv   # 20-question ground-truth dataset
```

---

## Dataset

`sec-edgar-eval-0` contains **20 questions** covering all 8 tools:

| Category | Questions | Difficulty |
|---|---|---|
| company_search | 2 | easy |
| company_resolution | 2 | easy |
| recent_filings | 2 | easy |
| annual_facts | 2 | medium |
| quarterly_facts | 2 | medium |
| concept_discovery | 2 | medium |
| cross_company_comparison | 2 | hard |
| filing_attribution | 2 | hard |
| multi_step_discovery | 2 | hard |
| edge_cases | 2 | easy/medium |

---

## Judges

| Judge | Function | Labels | Ground truth needed? |
|---|---|---|---|
| Correctness | `match_expected_response` | `correct` / `incorrect` | Yes |
| Scope | `check_answer_scope` | `within_scope` / `out_of_scope` | No |

Both judges use `JUDGE_MODEL` (set separately from `AGENT_MODEL` to reduce
self-preference bias). Default judge model: `claude_4_6_sonnet`.

---

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `USAI_API_KEY` | Yes | Model gateway API key |
| `USAI_BASE_URL` | Yes | Model gateway base URL |
| `AGENT_MODEL` | Yes | Model for the agent-under-test |
| `JUDGE_MODEL` | No | Model for LLM judges (default: `claude_4_6_sonnet`) |
| `MCP_ENDPOINT` | No | Override Code Engine MCP URL |
| `PHOENIX_ENDPOINT` | No | Phoenix server endpoint (default: `http://localhost:6006`) |
| `PHOENIX_PROJECT` | No | Phoenix project name (default: `sec-edgar-eval`) |

---

## Smoke-testing the agent

```bash
cd eval/phoenix
python agent.py
```

This runs one test question (`"What is the SIC code for Apple?"`) through the full
pipeline (MCP connection → tool call → response) and prints the result.

---

## Interpreting results

In the Phoenix UI (http://localhost:6006):

- **`correct` rate** — how often the agent returns factually accurate answers.
  Low scores indicate tool routing gaps or XBRL concept name issues.
- **`within_scope` rate** — how often the agent stays in its lane.
  `out_of_scope` hits on in-scope questions indicate refusal or hallucination.

For each failing trace:
1. Expand the LangChain span tree to see which tools were called.
2. If no tools fired → tighten the agent instructions in `agents/sec_edgar_agent.yaml`.
3. If wrong tool fired → check the question wording and agent routing rules.
4. If concept not found → confirm the agent tried `sec_edgar_list_concepts` as fallback.
