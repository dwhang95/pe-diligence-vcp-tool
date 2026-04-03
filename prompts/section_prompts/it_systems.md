# Prompt: IT & Systems Maturity

Generate the IT & Systems Maturity section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Research findings: {research_summary}

## Instructions

Middle market companies in the $50M–$500M EV range follow predictable IT maturity patterns based on ownership history, industry, and size. Use these patterns to form a directional hypothesis:

**Ownership history signals:**
- Founder-led, never PE-backed → likely: QuickBooks/Sage, Excel-heavy reporting, no real BI layer
- 1 prior PE sponsor → likely: partially upgraded ERP (NetSuite, Epicor, or similar), some KPI reporting, gaps in data integrity
- 2+ PE sponsors → likely: ERP exists, but integration tech debt from bolt-on acquisitions is the real risk

**Industry signals:**
- Industrial/manufacturing → ERP maturity is critical (MES, WMS often missing in lower middle market)
- Healthcare services → EMR/EHR complexity, HIPAA compliance layer
- Business services → CRM and billing system quality are the key assessment areas
- Consumer products → SKU proliferation management, ecomm integration, 3PL data feeds

**Size signals:**
- <$100M EV: expect significant reporting debt, manual processes
- $100M–$300M EV: ERP likely exists, BI layer often weak
- $300M–$500M EV: systems should be modernized; if not, that's a red flag in itself

Assess:
1. **ERP/Core Systems** — Hypothesis on what they're running and what that means
2. **Reporting & Data Maturity** — KPI access, board deck production method, data reliability
3. **Tech Debt Risk** — Integration issues, unsupported systems, custom code risk
4. **Digital/AI Enablement Potential** — What's realistically achievable in a hold period
5. **Systems Diligence Checklist** — 5–8 specific questions for IT diligence

## Format
```
## 3. IT & Systems Maturity

**ERP/Core Systems**
{Hypothesis + directional assessment}

**Reporting & Data Maturity**
{Assessment}

**Tech Debt Risk:** {Low/Medium/High}
{Assessment}

**Digital/AI Enablement Potential**
{What's realistic in 3–5 year hold}

**Systems Diligence Checklist**
1. {Question}
2. {Question}
...
```
