# Prompt: IT & Systems Maturity (Bullet Mode)

Generate the IT & Systems Maturity section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- Bullets only. No prose paragraphs.
- Every bullet maximum 25 words.
- Do not restate context already in the input.
- No hedging language ("it appears", "it seems", "may potentially").
- State the finding, then the implication. Nothing else.
- Maximum 4 findings total.

## Instructions

Use ownership history, industry, and EV range to form a directional IT hypothesis. Assess exactly 4 areas:

1. **ERP/Core Systems** — Hypothesis on what they're likely running and the key risk
2. **Reporting & Data Maturity** — KPI access, board reporting, data reliability
3. **Tech Debt Risk** (Low/Medium/High) — Integration issues, unsupported systems
4. **Digital/AI Enablement Potential** — What's realistically achievable in hold period

Each finding = 1 header + 1–2 bullets max. No diligence checklist in bullet mode.

## Format
```
## 3. IT & Systems Maturity

**ERP/Core Systems**
- {Hypothesis on system — max 25 words}
- {Key risk or implication — max 25 words}

**Reporting & Data Maturity**
- {Finding + implication — max 25 words}

**Tech Debt Risk: {Low/Medium/High}**
- {Finding + implication — max 25 words}

**Digital/AI Enablement Potential**
- {What's realistic in hold period — max 25 words}
```
