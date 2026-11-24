# Q5 — SEC EDGAR Agent Demo: Full Narrated Screen-Recording Script

**Target duration:** 8–10 minutes  
**Format:** Narrated screen recording of IBM watsonx Orchestrate Chat UI  
**Agent:** `sec_edgar_agent`  
**Voice-over style:** Clear, confident, conversational — speaking to a technical audience  

---

## PRE-RECORDING CHECKLIST

Before hitting record:
- [ ] WXO Chat open in browser, `sec_edgar_agent` selected
- [ ] Text editor or sticky note with the 8 prompts ready to copy-paste
- [ ] Microphone checked
- [ ] Notifications silenced
- [ ] Browser zoom at 100% or 110% for readability
- [ ] Previous conversation cleared (new chat thread)

---

## INTRO TITLE CARD  
*(0:00 – 0:30, ~30 seconds — optional: show a simple title slide or just go straight to screen)*

**[NARRATION]**

> "Hi, I'm Michael Schihl. This is a demo of the SEC EDGAR Facts Explorer — a project I built for the GSA MCP Hackathon. I'll show you eight questions, each answered by a live agent running on IBM watsonx Orchestrate, pulling real financial data directly from the SEC's EDGAR APIs. Every number you'll see is traceable back to the actual SEC filing it came from. Let's get started."

---

## SCENE 1 — Opening the Chat  
*(0:30 – 0:55, ~25 seconds)*

**[ACTION]**  
Show the IBM watsonx Orchestrate Chat interface. The agent `sec_edgar_agent` is selected and visible in the sidebar or header.

**[NARRATION]**

> "I'm in IBM watsonx Orchestrate, using the Chat interface. The agent you see here — `sec_edgar_agent` — is a native WXO agent backed by a 14-tool MCP server deployed to IBM Code Engine. The MCP server wraps SEC EDGAR's public APIs. No API keys needed — EDGAR is free and open. The agent calls the server, the server calls EDGAR, and the data flows back."

> "I'll ask eight questions that together cover all fourteen tools in the toolkit."

---

## STEP 1 — Company Name Search  
*(0:55 – 1:50, ~55 seconds)*

**[ACTION]**  
Type and send:
> `Find all companies with "Berkshire" in their name.`

Wait for the response (typically 3–5 seconds). The agent will return a table of Berkshire-related SEC registrants.

**[NARRATION — while typing]**

> "Step one: a simple company name search. I'll ask for all companies with 'Berkshire' in their name."

**[NARRATION — while response loads]**

> "The agent is calling `sec_edgar_search_companies` on the SEC's EDGAR full company index — that's roughly ten thousand exchange-listed entities searched in real time."

**[NARRATION — after response appears, pointing at screen]**

> "Notice we get back multiple rows. There's Berkshire Hathaway Energy, Berkshire Hathaway Inc itself — listed with both its BRK-A and BRK-B share classes under the same CIK — and several smaller companies with 'Berkshire' in the name. 

> This is important for a real research workflow: large conglomerates can appear as multiple SEC registrants — holding companies, operating subsidiaries, finance subsidiaries. The agent surfaces all of them and lets you choose. Each row has the SEC's internal CIK identifier, which is the stable key all the other tools use."

---

## STEP 2 — Resolve by Ticker  
*(1:50 – 2:45, ~55 seconds)*

**[ACTION]**  
Type and send:
> `What is the SEC CIK number, SIC code, and state of incorporation for Microsoft (MSFT)?`

**[NARRATION — while typing]**

> "Step two: given a ticker, resolve the full SEC registration record."

**[NARRATION — while response loads]**

> "The agent is calling `sec_edgar_resolve_company` — this hits the SEC's EDGAR submissions endpoint and returns the authoritative identity record."

**[NARRATION — after response appears]**

> "Microsoft: CIK 0000789019, SIC code 7372 — 'Services-Prepackaged Software,' incorporated in Washington state. This is the SEC's own record, not a data vendor's interpretation.

> Notice the SIC code — that's the Standard Industrial Classification used by the SEC to categorize companies by industry. We'll see that code again in Step 7 when we do an industry screen. The CIK is the key I'll use in the next few steps to pull filing history and financial data."

---

## STEP 3 — Recent Filings  
*(2:45 – 3:45, ~60 seconds)*

**[ACTION]**  
Type and send:
> `List the five most recent 10-K filings for Microsoft.`

**[NARRATION — while typing]**

> "Step three: filing history. I want the last five annual reports — the 10-Ks — for Microsoft."

**[NARRATION — while response loads]**

> "The agent is calling `sec_edgar_get_recent_filings` with `form_type='10-K'` and `limit=5`."

**[NARRATION — after response appears]**

> "Five rows: each one shows the filing date, the report period end date, and the accession number. That accession number is the SEC's universal filing key — it looks like a long hyphenated number, and it appears in EDGAR URLs and in every financial data row we'll see later.

> Notice Microsoft's fiscal year ends June 30, so their 10-K always arrives in late July. The same tool works for 10-Q quarterly reports, 8-K current reports, DEF 14A proxy statements — any form type. If I passed `form_type=''`, I'd get every recent filing regardless of type.

> I'll use one of these accession numbers in Step 8 to open the actual filing."

---

## STEP 4 — Annual Financial Facts  
*(3:45 – 4:50, ~65 seconds)*

**[ACTION]**  
Type and send:
> `Show me the last 5 annual net income figures for Apple.`

**[NARRATION — while typing]**

> "Step four: multi-year financial history. I'll ask for Apple's annual net income over the last five fiscal years."

**[NARRATION — while response loads]**

> "This calls `sec_edgar_get_company_fact` — it hits the SEC's XBRL company-facts endpoint, which is the machine-readable financial data the SEC compiles from every company's tagged annual and quarterly reports.

> XBRL — the eXtensible Business Reporting Language — is the system companies use to tag individual line items in their financial statements. 'NetIncomeLoss' is the XBRL tag for net income."

**[NARRATION — after response appears]**

> "Five years of Apple net income, all from EDGAR. Notice each row includes the fiscal year, the dollar amount, the form type — 10-K — and the accession number of the specific filing that reported it.

> Apple's most recent fiscal year — FY 2026 — shows $132 billion in net income. That's the number directly from the 10-K Apple filed with the SEC.

> One thing that took real engineering to get right: the SEC's XBRL data stores fiscal year values on the *filing date*, not the reporting period. If you use the wrong field, you'll label FY2023 net income as FY2024. I fixed that by deriving the fiscal year from the period-end date, which is always accurate."

---

## STEP 5 — Quarterly Revenue Trend  
*(4:50 – 5:55, ~65 seconds)*

**[ACTION]**  
Type and send:
> `Show me Apple's quarterly revenue for the last 8 quarters.`

**[NARRATION — while typing]**

> "Step five: quarterly trends. I want eight quarters of Apple revenue — not annual, true single-quarter figures."

**[NARRATION — while response loads]**

> "This calls `sec_edgar_get_quarterly_facts`. The tricky part here: the SEC XBRL API stores *both* single-quarter three-month values *and* year-to-date cumulative values under the exact same period label. The API calls them both 'Q3' — but one is a three-month figure and the other is a nine-month running total.

> My server fixes this by computing the duration of each observation — end date minus start date — and only accepting values in the 80-to-100-day window. Nine-month YTD values are 270 days; they get filtered out."

**[NARRATION — after response appears]**

> "Eight quarters of genuine single-quarter revenue. Q3 FY2026 shows about $109 billion — that's the three-month figure, which is correct. Before my fix, that number would have read $364 billion — the nine-month YTD total — a 3× error.

> Notice Q4 is handled differently: Apple doesn't file a 10-Q for fiscal Q4. That quarter only appears in the annual 10-K. My server derives Q4 by computing annual FY minus the nine-month YTD, and labels it '(derived)' so it's transparent.

> Apple's fiscal year runs October through September, so Q1 is the holiday quarter — you can see it's the highest revenue quarter each year at around $124 billion."

---

## STEP 6 — XBRL Concept Discovery  
*(5:55 – 6:40, ~45 seconds)*

**[ACTION]**  
Type and send:
> `What revenue-related XBRL concepts does Apple report in us-gaap?`

**[NARRATION — while typing]**

> "Step six: XBRL concept discovery. XBRL tag names are not obvious — 'revenue' might be `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, or something else entirely depending on the company and the year."

**[NARRATION — while response loads]**

> "The agent is calling `sec_edgar_list_concepts` with the keyword 'revenue'."

**[NARRATION — after response appears]**

> "Seven matching concepts. Notice Apple uses `RevenueFromContractWithCustomerExcludingAssessedTax` as the primary revenue tag — that's the post-2018 ASC 606 label. But `Revenues` and the older deprecated `SalesRevenueNet` are also present for historical filings.

> This is the escape hatch when you get a 'concept not found' error. You can always browse what a specific company actually reports. Try searching 'debt' on Tesla — you'll see 72 matching concepts covering convertible notes, finance leases, and long-term obligations."

---

## STEP 7 — Cross-Company Comparison  
*(6:40 – 7:35, ~55 seconds)*

**[ACTION]**  
Type and send:
> `Compare the most recent annual net income for Apple, Microsoft, and Google.`

**[NARRATION — while typing]**

> "Step seven: cross-company comparison. One call, three companies, one XBRL concept."

**[NARRATION — while response loads]**

> "The agent is calling `sec_edgar_compare_companies` with all three identifiers. Watch for the comparability warning — this is an important feature."

**[NARRATION — after response appears]**

> "Three of the most profitable companies in the world. Apple at $132 billion, Microsoft at $134 billion, Alphabet at $132 billion. Strikingly close.

> But look at the warning the agent surfaced: the fiscal year ends don't align. Apple's fiscal year ends in September, Microsoft's in June, and Alphabet's in December. These aren't the same twelve-month window — you're not comparing like-for-like periods.

> This warning is not optional — the agent instructions require it whenever fiscal year ends differ across compared companies. I tested this in both directions: on a JPMorgan vs. Bank of America comparison where both fiscal years end December 31, the agent correctly omits the warning because it's not needed. The warning only appears when it's genuinely warranted."

---

## STEP 8 — Source Filing Attribution  
*(7:35 – 8:30, ~55 seconds)*

**[ACTION]**  
Type and send:
> `Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link.`

**[NARRATION — while typing]**

> "Step eight: source attribution. Every number this agent returns includes the accession number of the filing it came from. I'll ask it to close that provenance chain — go from the data point all the way back to the actual SEC filing."

**[NARRATION — while response loads]**

> "The agent is first calling `sec_edgar_get_company_fact` to get the most recent annual revenue observation and its accession number, then calling `sec_edgar_get_filing_metadata` to resolve that accession number to the full filing record."

**[NARRATION — after response appears]**

> "Accession number 0000320193-26-000026. Form 10-K. Filed November 3, 2026. Period ending September 26, 2026. Revenue $478.8 billion for fiscal year 2026.

> And there's the EDGAR link. That URL is not constructed by the agent — it comes directly from the tool's return value. The agent instructions explicitly prohibit constructing or guessing URLs. Every link in every response must be a tool-returned value. This is what makes it verifiable.

> Let me open that link—"

**[ACTION]**  
Click the EDGAR link in the agent response. It opens Apple's 10-K filing in the SEC's EDGAR viewer.

**[NARRATION — with filing open in browser]**

> "And there it is — Apple's 10-K filing on SEC.gov. The URL contains the CIK — 320193 — and the accession number, embedded directly. No guessing. This is the full provenance chain: user question → XBRL concept → 10-K filing → audited financial statement.

> This is the core value proposition: every financial number this agent returns is traceable back to a primary source document that you can open and verify right now."

---

## CLOSING  
*(8:30 – 9:00, ~30 seconds)*

**[ACTION]**  
Return to the WXO chat window showing the conversation history.

**[NARRATION]**

> "That's eight questions, all answered with live data from the SEC's EDGAR APIs. The agent covered name search, company resolution, filing history, annual financial facts, quarterly trends, XBRL concept discovery, cross-company comparison, and source attribution.

> The MCP server behind this has fourteen tools, 198 company synonyms, and an XBRL concept resolver covering 7,462 FASB taxonomy entries. It's deployed as an always-warm HTTPS service on IBM Code Engine — no cold starts.

> Every evaluation benchmark question — thirty-nine of them — passed: 100% tool routing, 100% scope, all eight numeric anchors. The evaluation code, benchmark questions, and agent definition are all in the GitHub repository linked in the submission.

> Thanks for watching."

---

## OPTIONAL BONUS SEGMENT (if time allows, after Step 8)

**[ACTION]**  
Type and send:
> `List semiconductor companies on NASDAQ (SIC 3674).`

**[NARRATION]**

> "Bonus: the screening tool. SIC code 3674 is 'Semiconductors and Related Devices.' I'll ask for NASDAQ-listed semiconductor companies."

After response:
> "The agent called `sec_edgar_screen` using the SEC's browse-edgar data, returning companies by SIC and exchange. Intel, Nvidia, Broadcom — all in one query, with CIK and ticker. This is useful for discovery when you don't know the ticker but know the industry."

---

## RECORDING TIPS

| Timing issue | Fix |
|---|---|
| Response takes >15 seconds | Normal for multi-step chains; fill with narration about what tool is running |
| Agent asks a clarifying question | Type the qualifier directly — e.g. add "us-gaap" or the exact ticker |
| Step 6 returns fewer concepts | The agent may have searched a different keyword; acceptable for the demo |
| EDGAR link doesn't open | Show the accession number and explain the URL structure verbally |
| WXO session expired | Run: `source .env && venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |

## POST-RECORDING

- Trim silence at start/end
- Encode as MP4, H.264, 1080p
- Target file size: 30–40 MB at 8 minutes (well under the 50 MB Q5 limit)
- File name: `Q5_sec_edgar_demo.mp4`
