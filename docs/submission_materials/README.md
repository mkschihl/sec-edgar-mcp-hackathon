# Submission Materials — GSA MCP Hackathon 2026

**Author:** Michael Schihl  
**Prepared:** 2026-11-23 (Session 17)  
**Status: PREPARED — do not submit yet**

---

## Form questions and answers

### Q1 — Project name
**SEC EDGAR Facts Explorer**

### Q2 — Author name
**Michael Schihl**

### Q3 — Track selection
**Check BOTH "Service: Read" AND "Data"**

**Rationale:**

- **"Service: Read"** is the primary fit. This project exposes a live external read-only service (SEC EDGAR's public REST APIs) as a structured MCP toolkit with 14 tools. The MCP server wraps 4 distinct EDGAR API endpoints and makes them available to any MCP client. That is exactly what a "Service: Read" MCP server does.
- **"Data"** is also valid. The server makes structured government financial data (XBRL company facts, 7,462 US-GAAP concepts, 10-K/10-Q/8-K filing metadata) machine-readable for AI agents. It transforms raw EDGAR JSON into clean, typed, deduplicated fact rows.
- **Do NOT check "Service: Write"** — this server makes no writes to any system.

If only one track is allowed: **Service: Read** is the stronger fit because the primary innovation is the MCP server architecture (14 tools, remote streamable-HTTP transport, XBRL concept resolver, synonym table), not the data itself.

---

### Q4 — One-sentence description

> "I built an MCP server and watsonx Orchestrate agent that answers questions about public company SEC filings — things like 'What was Apple's revenue last quarter?' or 'Which filing first reported Microsoft's most recent net income?' — by calling the SEC's official EDGAR APIs directly, so every number is traceable back to the primary source."

**Shorter version (under 30 words, if form has a character limit):**
> "An MCP server and watsonx Orchestrate agent that answers financial questions about public companies by calling the SEC's EDGAR APIs directly — every number traceable to the source filing."

---

### Q5 — Video demo upload
**File to upload:** Record from the script at `docs/submission_materials/Q5_video_script.md`  
**Target format:** MP4, H.264, 1080p  
**Target file size:** ~30–40 MB at 8 minutes (well under the 50 MB limit)  
**Suggested filename:** `Q5_sec_edgar_demo.mp4`

The script is a complete, second-by-second narrated voice-over script for an 8–10 minute recording covering all 8 demo steps (14 tools total), with exact prompts, narration text, and recording tips.

---

### Q6 — Evaluation report upload
**Source:** `evaluation/EVAL_REPORT.md` + `evaluation/interpretation.md`  
**HTML artifact:** "Q6 — SEC EDGAR Agent Evaluation Report" (open in browser → Print → Save as PDF)  
**Suggested filename:** `Q6_evaluation_report.pdf`

The report covers:
- Executive summary (39/39 pass, 100%)
- Full per-question results table (39 rows)
- Tool utilisation table (14 tools)
- Results by category (19 categories)
- 3-layer evaluation methodology
- 7 issues found and fixed
- LLM-as-judge experiment history

---

### Q7 — Slide deck upload
**HTML artifact:** "Q7 — SEC EDGAR Facts Explorer: Slide Deck" (open in browser → Print → Save as PDF)  
**Suggested filename:** `Q7_slide_deck.pdf`

11 slides covering:
1. Title / key metrics
2. Problem statement
3. Architecture diagram
4. 14 MCP tools
5. Key technical decisions (6 decisions)
6. Evaluation results (39/39)
7. Issues found and fixed (7 issues)
8. Demo highlights (8 steps)
9. Project milestones (11 milestones)
10. Next steps
11. Closing / repo URL

---

### Q8 — Code link upload
**HTML artifact:** "Q8 — SEC EDGAR Facts Explorer: Code Repository" (open in browser → Print → Save as PDF)  
**Suggested filename:** `Q8_code_link.pdf`  
**Repo URL:** https://github.com/mkschihl/wxo-agentic-workflow

---

## How to convert HTML artifacts to PDF

1. Open the artifact in your browser (click "Open" on the artifact tile)
2. Press **Cmd+P** (Mac) or **Ctrl+P** (Windows)
3. Choose **"Save as PDF"** or **"Print to PDF"**
4. For the slide deck: set orientation to **Portrait**, margins to **None** or **Minimum**
5. Save with the suggested filename above

---

## Files in this directory

| File | Purpose |
|------|---------|
| `README.md` | This file — submission checklist and Q3/Q4 answers |
| `Q5_video_script.md` | Complete narrated voice-over script for the video demo |

HTML artifacts (open from chat, print to PDF):
- Q6 — Evaluation Report
- Q7 — Slide Deck  
- Q8 — Code Repository Link

---

## Submission form URL (do not open until ready to submit)

https://feedback.gsa.gov/jfe/form/SV_8ka3AgXZK282mto?Q_DL=jxfb83Ar5DXYwdM_8ka3AgXZK282mto_CGC_hN5dg4bI3c9NNPD&Q_CHL=email
