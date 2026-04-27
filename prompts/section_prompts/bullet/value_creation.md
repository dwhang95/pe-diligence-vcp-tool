# Prompt: Value Creation Opportunities (Bullet Mode)

Generate the Value Creation Opportunities section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- Maximum 5 levers. Highest-confidence, highest-impact first.
- Each lever = 1 name line + confidence + EBITDA impact estimate + 1 bullet rationale only.
- Rationale bullet maximum 25 words.
- No hedging language. No generic statements.
- Do not restate context already in the input.

## Instructions

Identify the 5 highest-impact operational value creation levers. Categories: Revenue Growth, Cost Reduction, Working Capital, Organizational Effectiveness, Digital/AI Transformation.

For each lever:
- Name | Category | Timeline | Confidence (High/Med/Low) | Est. EBITDA impact
- One rationale bullet (max 25 words): specific hypothesis, not generic commentary

Confidence calibration:
- High: consistent with company profile AND supported by research data
- Medium: reasonable hypothesis given industry/size/ownership, limited direct evidence
- Low: speculative but worth validating

## Format
```
## 4. Value Creation Opportunities

| # | Lever | Category | Timeline | Confidence | Est. EBITDA Impact |
|---|---|---|---|---|---|
| 1 | {{lever name}} | {{category}} | {{0–12 / 12–24 / 24–36 mo}} | {{High/Med/Low}} | {{e.g. +$1–2M}} |
| 2 | ... |
| 3 | ... |
| 4 | ... |
| 5 | ... |

**1. {{Lever Name}}**
- {{Specific rationale — max 25 words}}

**2. {{Lever Name}}**
- {{Specific rationale — max 25 words}}

[Repeat for all 5 levers]
```
