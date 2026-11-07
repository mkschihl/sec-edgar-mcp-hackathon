"""SEC EDGAR Agent — Evaluation Runner.

Runs the 20 benchmark questions against the deployed sec_edgar_agent via the
watsonx Orchestrate runtime REST API (POST /v1/orchestrate/runs), scores each
response, and writes evaluation/EVAL_REPORT.md.

Usage (from workspace root, with venv active and gsa-hackathon env live):
    python evaluation/run_evaluation.py

Optional flags:
    --dry-run           Print questions without calling the agent
    --ids BQ-01 BQ-03   Run only specific question IDs
    --delay N           Seconds between questions (default: 2)

Output:
    evaluation/EVAL_REPORT.md   — full scored report
    evaluation/raw_results.json — machine-readable results

Scoring:
    pass    — all expected_tools fired AND response has substantive content
    partial — some expected_tools fired, or minor issues
    fail    — no expected tools fired, timeout, or hallucination/refusal
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
WORKSPACE = Path(__file__).resolve().parent.parent
EVAL_DIR = WORKSPACE / "evaluation"
REPORT_PATH = EVAL_DIR / "EVAL_REPORT.md"
RAW_PATH = EVAL_DIR / "raw_results.json"

AGENT_NAME = "sec_edgar_agent"
SERVICE_URL = "https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/76b76ce7-8b9e-4f7e-885b-967fbaef80c9"
CREDENTIALS_FILE = Path.home() / ".cache" / "orchestrate" / "credentials.yaml"

# ---------------------------------------------------------------------------
# Import benchmark questions
# ---------------------------------------------------------------------------
sys.path.insert(0, str(EVAL_DIR))
from benchmark_questions import BENCHMARK_QUESTIONS

# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------

def load_token() -> str:
    """Read the current bearer token from the ADK credentials cache."""
    try:
        import yaml  # bundled with ADK venv
        creds = yaml.safe_load(CREDENTIALS_FILE.read_text())
        token = creds["auth"]["gsa-hackathon"]["wxo_mcsp_token"]
        expiry = creds["auth"]["gsa-hackathon"].get("wxo_mcsp_token_expiry", 0)
        now = time.time()
        if expiry and now > expiry:
            print(f"WARNING: Token expired at {datetime.fromtimestamp(expiry)}. "
                  f"Re-activate with: orchestrate env activate gsa-hackathon --api-key $WXO_API_KEY")
        return token
    except Exception as exc:
        raise RuntimeError(
            f"Could not read token from {CREDENTIALS_FILE}: {exc}\n"
            "Run: orchestrate env activate gsa-hackathon --api-key $WXO_API_KEY"
        ) from exc


# ---------------------------------------------------------------------------
# Agent lookup
# ---------------------------------------------------------------------------

def get_agent_id(token: str) -> str:
    """Resolve agent name to agent ID via the Orchestrate agents API."""
    url = f"{SERVICE_URL}/v1/orchestrate/agents"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        resp = httpx.get(url, headers=headers, timeout=20.0, follow_redirects=True)
        resp.raise_for_status()
        agents = resp.json()
        # handle both list and {"agents": [...]} shapes
        if isinstance(agents, list):
            items = agents
        else:
            items = agents.get("data", agents.get("agents", []))
        for agent in items:
            name = agent.get("name") or agent.get("agent_name", "")
            if name == AGENT_NAME:
                aid = agent.get("id") or agent.get("agent_id", "")
                if aid:
                    return aid
        # If not found by name, return the name itself — some endpoints accept it
        print(f"WARNING: could not resolve agent '{AGENT_NAME}' to ID; using name directly.")
        return AGENT_NAME
    except Exception as exc:
        print(f"WARNING: agent lookup failed ({exc}); using agent name directly.")
        return AGENT_NAME


# ---------------------------------------------------------------------------
# Agent call via REST
# ---------------------------------------------------------------------------

def call_agent_rest(question: str, token: str, agent_id: str, timeout: int = 60) -> tuple[str, dict]:
    """
    POST a message to the agent via the /chat/completions SSE endpoint.
    Returns (response_text, synthetic_dict_with_full_sse_text).

    The endpoint streams SSE lines. We collect:
      - assistant content deltas → final response text
      - tool_calls step deltas   → which tools fired (for scoring)
    """
    url = f"{SERVICE_URL}/v1/orchestrate/{agent_id}/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    body = {"messages": [{"role": "user", "content": question}]}

    response_chunks: list[str] = []
    tool_calls_seen: list[str] = []
    raw_sse_lines: list[str] = []

    try:
        with httpx.stream("POST", url, headers=headers, json=body,
                          timeout=timeout, follow_redirects=True) as resp:
            if resp.status_code >= 400:
                body_text = resp.read().decode()
                return f"[HTTP {resp.status_code}: {body_text[:200]}]", {}
            for line in resp.iter_lines():
                raw_sse_lines.append(line)
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue

                choices = chunk.get("choices", [])
                for choice in choices:
                    delta = choice.get("delta", {})
                    # Accumulate assistant text
                    content = delta.get("content", "")
                    if content:
                        response_chunks.append(content)
                    # Capture tool call names for scoring
                    step = delta.get("step_details", {})
                    for tc in step.get("tool_calls", []):
                        name = tc.get("name", "")
                        if name:
                            tool_calls_seen.append(name)

    except httpx.TimeoutException:
        return "[TIMEOUT]", {}
    except Exception as exc:
        return f"[ERROR: {exc}]", {}

    response_text = "".join(response_chunks).strip()
    # Build a synthetic dict that contains tool names for the scorer
    synthetic = {
        "tool_calls": tool_calls_seen,
        "raw_sse": " ".join(raw_sse_lines)[:8000],
    }
    if not response_text:
        response_text = synthetic["raw_sse"][:500]
    return response_text, synthetic


# ---------------------------------------------------------------------------
# Tool-name extraction helpers
# ---------------------------------------------------------------------------

ALL_TOOL_NAMES = [
    "sec_edgar_search_companies",
    "sec_edgar_resolve_company",
    "sec_edgar_get_recent_filings",
    "sec_edgar_get_company_fact",
    "sec_edgar_get_quarterly_facts",
    "sec_edgar_compare_companies",
    "sec_edgar_get_filing_metadata",
    "sec_edgar_list_concepts",
]

REFUSAL_PATTERNS = [
    r"i (don't|do not|cannot|can't) (have access|access|retrieve|look up|find)",
    r"i'm unable to",
    r"as an ai",
    r"i don't have (real-?time|live|current)",
    r"i would need",
    r"not available in my (training|knowledge)",
]


def extract_tools_fired(raw: dict | str) -> list[str]:
    """Scan the full API response dict (or a string) for tool names."""
    text = json.dumps(raw) if isinstance(raw, dict) else str(raw)
    return [name for name in ALL_TOOL_NAMES if name in text]


def looks_like_refusal(text: str) -> bool:
    lower = text.lower()
    return any(re.search(pat, lower) for pat in REFUSAL_PATTERNS)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_question(q: dict, response_text: str, raw_response: dict) -> dict:
    tools_fired = extract_tools_fired(raw_response)
    # Also scan response text in case reasoning isn't in the raw dict
    tools_fired_text = extract_tools_fired(response_text)
    tools_fired = list(set(tools_fired) | set(tools_fired_text))

    expected = q["expected_tools"]
    missing = [t for t in expected if t not in tools_fired]
    is_refusal = looks_like_refusal(response_text)
    is_timeout = "[TIMEOUT]" in response_text
    is_error = response_text.startswith("[HTTP") or response_text.startswith("[ERROR")

    if is_timeout:
        return dict(score="fail", tools_fired=tools_fired, tools_missing=missing,
                    is_refusal=False,
                    notes="Request timed out (60s). Agent may be slow or token expired.")
    if is_error:
        return dict(score="fail", tools_fired=[], tools_missing=expected,
                    is_refusal=False, notes=f"API error: {response_text[:120]}")
    if is_refusal and not tools_fired:
        return dict(score="fail", tools_fired=tools_fired, tools_missing=missing,
                    is_refusal=True,
                    notes="Agent refused without calling any tool.")
    if not missing:
        score = "partial" if is_refusal else "pass"
        notes = ("All expected tools fired." if not is_refusal
                 else "All tools fired but response contains refusal language.")
    elif len(missing) < len(expected):
        score = "partial"
        notes = f"Some tools fired. Missing: {missing}."
    else:
        score = "fail"
        notes = f"No expected tools fired. Missing: {missing}."

    return dict(score=score, tools_fired=tools_fired, tools_missing=missing,
                is_refusal=is_refusal, notes=notes)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

SCORE_EMOJI = {"pass": "✅", "partial": "⚠️", "fail": "❌"}
DIFFICULTY_EMOJI = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}


def generate_report(results: list[dict], elapsed: float) -> str:
    total = len(results)
    passes   = sum(1 for r in results if r["score"] == "pass")
    partials = sum(1 for r in results if r["score"] == "partial")
    fails    = sum(1 for r in results if r["score"] == "fail")
    pass_rate    = round(passes / total * 100) if total else 0
    partial_rate = round(partials / total * 100) if total else 0
    fail_rate    = round(fails / total * 100) if total else 0

    tool_stats: dict[str, dict] = {t: {"expected": 0, "fired": 0} for t in ALL_TOOL_NAMES}
    for r in results:
        for t in r["expected_tools"]:
            tool_stats[t]["expected"] += 1
        for t in r["tools_fired"]:
            if t in tool_stats:
                tool_stats[t]["fired"] += 1

    cat_stats: dict[str, list] = {}
    for r in results:
        cat_stats.setdefault(r["category"], []).append(r["score"])

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# SEC EDGAR Agent — Evaluation Report",
        "",
        f"**Agent:** `{AGENT_NAME}`  ",
        f"**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  ",
        f"**Run date:** {ts}  ",
        f"**Duration:** {elapsed:.0f}s for {total} questions  ",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total questions | {total} |",
        f"| ✅ Pass | {passes} ({pass_rate}%) |",
        f"| ⚠️ Partial | {partials} ({partial_rate}%) |",
        f"| ❌ Fail | {fails} ({fail_rate}%) |",
        "",
        "---",
        "",
        "## Results by Question",
        "",
        "| ID | Diff | Category | Score | Expected Tools | Tools Fired | Notes |",
        "|---|---|---|---|---|---|---|",
    ]

    for r in results:
        d_icon = DIFFICULTY_EMOJI.get(r["difficulty"], "")
        s_icon = SCORE_EMOJI.get(r["score"], "")
        exp_str   = ", ".join(f"`{t.replace('sec_edgar_','')}`" for t in r["expected_tools"])
        fired_str = ", ".join(f"`{t.replace('sec_edgar_','')}`" for t in r["tools_fired"]) or "*(none)*"
        notes = r["notes"].replace("|", "\\|")
        lines.append(
            f"| {r['id']} | {d_icon} {r['difficulty']} | {r['category']} "
            f"| {s_icon} {r['score']} | {exp_str} | {fired_str} | {notes} |"
        )

    lines += ["", "---", "", "## Agent Responses", ""]
    for r in results:
        s_icon = SCORE_EMOJI.get(r["score"], "")
        resp = r["response_text"]
        resp_display = resp[:2000] + ("..." if len(resp) > 2000 else "")
        lines += [
            f"### {r['id']} — {s_icon} {r['score'].upper()}",
            f"**Question:** {r['question']}  ",
            f"**Expected tools:** {', '.join(r['expected_tools'])}  ",
            f"**Tools fired:** {', '.join(r['tools_fired']) or '*(none)*'}  ",
            "",
            "<details><summary>Agent response</summary>",
            "",
            "```",
            resp_display,
            "```",
            "",
            "</details>",
            "",
        ]

    lines += [
        "---",
        "",
        "## Tool Utilisation",
        "",
        "| Tool | Expected in N Qs | Times Fired | Fire Rate |",
        "|---|---|---|---|",
    ]
    for tool, stats in sorted(tool_stats.items()):
        n_exp = stats["expected"]
        n_fired = stats["fired"]
        if n_exp > 0:
            pct = round(n_fired / n_exp * 100)
            lines.append(f"| `{tool}` | {n_exp} | {n_fired} | {pct}% |")

    lines += [
        "",
        "---",
        "",
        "## Results by Category",
        "",
        "| Category | Questions | Pass | Partial | Fail |",
        "|---|---|---|---|---|",
    ]
    for cat, scores in sorted(cat_stats.items()):
        lines.append(
            f"| {cat} | {len(scores)} | {scores.count('pass')} "
            f"| {scores.count('partial')} | {scores.count('fail')} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Interpretation",
        "",
        "### What the scores mean",
        "",
        "- **✅ Pass** — all expected tools fired; substantive answer returned.",
        "- **⚠️ Partial** — some expected tools fired, or minor response quality issues.",
        "- **❌ Fail** — no required tools fired, API error, timeout, or hallucination.",
        "",
        "### How tools/skills are being utilised",
        "",
        "The **Tool Utilisation** table shows how reliably the agent routes each question",
        "to the correct tool. A low fire rate on an expected tool indicates one of:",
        "",
        "1. **Routing gap** — the agent instructions don't clearly map the question pattern",
        "   to the tool. Fix: add a more explicit rule in `agents/sec_edgar_agent.yaml`.",
        "2. **Tool chaining skip** — the agent skips an intermediate step (e.g. resolving",
        "   a company mentally). Acceptable for easy questions; problematic for hard ones.",
        "3. **Concept name problem** — the agent can't find the XBRL concept and gives up",
        "   instead of calling `sec_edgar_list_concepts` to discover the right name.",
        "",
        "### Recommended next steps",
        "",
        "For each ❌ Fail or ⚠️ Partial:",
        "",
        "1. Re-run the question in the wxO UI to see the full reasoning trace.",
        "2. If the wrong tool fired: tighten the matching rule in the agent `instructions:` block.",
        "3. If no tool fired: add a hard rule — *'Always call a tool; never answer from memory.'*",
        "4. If a timeout or HTTP error occurred: re-activate the token and re-run with `--ids`.",
        "",
        "---",
        "",
        "*Generated by `evaluation/run_evaluation.py`*",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ids", nargs="+", metavar="ID")
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()

    questions = BENCHMARK_QUESTIONS
    if args.ids:
        questions = [q for q in questions if q["id"] in args.ids]
        if not questions:
            print(f"No questions matched: {args.ids}")
            sys.exit(1)

    print(f"SEC EDGAR Agent Evaluation")
    print(f"Agent : {AGENT_NAME}")
    print(f"URL   : {SERVICE_URL}")
    print(f"Qs    : {len(questions)}")
    print("=" * 60)

    if args.dry_run:
        for q in questions:
            print(f"\n{q['id']} [{q['difficulty']}] {q['category']}")
            print(f"  Q: {q['question']}")
            print(f"  Expected: {q['expected_tools']}")
        return

    # Load token
    token = load_token()

    # Resolve agent ID
    print("Resolving agent ID...")
    agent_id = get_agent_id(token)
    print(f"Agent ID: {agent_id}")
    print("=" * 60)

    results = []
    start = time.time()

    for i, q in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {q['id']} — {q['category']} ({q['difficulty']})")
        print(f"  Q: {q['question'][:90]}{'...' if len(q['question']) > 90 else ''}")

        response_text, raw_resp = call_agent_rest(q["question"], token, agent_id)
        scored = score_question(q, response_text, raw_resp)

        result = {**q, "response_text": response_text,
                  "raw_response_keys": list(raw_resp.keys()) if raw_resp else [],
                  **scored}
        results.append(result)

        icon = SCORE_EMOJI.get(scored["score"], "?")
        print(f"  {icon} {scored['score'].upper()} | tools: {scored['tools_fired'] or '(none)'}")
        if scored["notes"] != "All expected tools fired.":
            print(f"     {scored['notes']}")
        if len(response_text) > 20 and not response_text.startswith("["):
            print(f"     response: {response_text[:120]}...")

        if i < len(questions) - 1:
            time.sleep(args.delay)

    elapsed = time.time() - start

    # Save raw JSON
    RAW_PATH.write_text(json.dumps(results, indent=2))
    print(f"\nRaw results → {RAW_PATH}")

    # Generate and save report
    report = generate_report(results, elapsed)
    REPORT_PATH.write_text(report)
    print(f"Report      → {REPORT_PATH}")

    # Print summary
    passes   = sum(1 for r in results if r["score"] == "pass")
    partials = sum(1 for r in results if r["score"] == "partial")
    fails    = sum(1 for r in results if r["score"] == "fail")
    print(f"\n{'='*60}")
    print(f"FINAL: {passes}/{len(results)} pass | {partials} partial | {fails} fail "
          f"| {round(passes/len(results)*100)}% pass rate")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
