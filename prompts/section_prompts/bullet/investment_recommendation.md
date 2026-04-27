# Prompt: Investment Recommendation (Bullet Mode)

Generate the Investment Recommendation section for the PE ops diligence brief.

## Input Context
- Company: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Context notes: {context_notes}
- Research findings: {research_summary}
- Executive summary: {exec_summary_text}
- Risk flags: {risk_flags_summary}
- Value creation opportunities: {value_creation_summary}

## Format Rules — STRICTLY ENFORCE
- Verdict + 3 reasons + 3 conditions = bullets only. No prose paragraphs.
- Every bullet maximum 25 words.
- No hedging language. Clear directional verdict.
- Reference actual characteristics of this company — not generic PE commentary.
- Do not restate context already in the input.

## Instructions

Deliver a clear operational verdict. Choose exactly one: **Pursue** / **Pursue with Conditions** / **Pass**.

Provide:
- 1-line verdict statement
- 3 bullets: strongest reasons supporting the verdict (specific to this company)
- 3 bullets: binary conditions to confirm before IC (fact-finding, not process steps)

No "Next Diligence Steps" section in bullet mode — the diligence questions section covers this.

## Format
```
## Investment Recommendation

### Verdict: {{Pursue / Pursue with Conditions / Pass}}
{{One-sentence statement — max 25 words}}

### Why
- {{Reason 1 — specific to this company, max 25 words}}
- {{Reason 2 — specific to this company, max 25 words}}
- {{Reason 3 — specific to this company, max 25 words}}

### Must Confirm Before IC
- {{Binary condition 1 — specific fact to confirm, max 25 words}}
- {{Binary condition 2 — specific fact to confirm, max 25 words}}
- {{Binary condition 3 — specific fact to confirm, max 25 words}}
```
