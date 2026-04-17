# Prompt: Investment Recommendation

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

## Instructions

Deliver a clear directional verdict on this deal from an operational standpoint. This is not a balanced summary — it is a point of view. No hedging.

**Verdict**
Choose exactly one: **Pursue** / **Pursue with Conditions** / **Pass**

State the verdict in one sentence. If "Pursue with Conditions," name the conditions directly.

**Top 3 Reasons Supporting the Recommendation**
The 3 strongest arguments for your verdict.
- For "Pursue": why the thesis is operationally compelling and executable.
- For "Pass": why the ops risk profile is unacceptable or the thesis is not supported.
- For "Pursue with Conditions": the upside that justifies working through the conditions.

Be specific. Reference actual characteristics of this company — not generic PE commentary. Avoid "strong management team" without supporting evidence.

**Top 3 Conditions to Validate Before IC**
Binary questions: each one either confirms the thesis or kills it.
Not process steps ("check references") — specific fact-finding: "Confirm top customer (est. 30% revenue) is on multi-year contract with auto-renewal past 2027 before advancing."

**Suggested Next Diligence Steps**
3–5 specific next steps, in priority order. Include the recommended owner (ops team, financial team, legal, third-party quality of earnings, specialist consultant).

## Format

### Verdict: [Pursue / Pursue with Conditions / Pass]
[One-sentence statement]

### Why
1. [Reason]
2. [Reason]
3. [Reason]

### Must Confirm Before IC
1. [Condition]
2. [Condition]
3. [Condition]

### Next Diligence Steps
1. [Step] — [Owner]
2. [Step] — [Owner]
3. [Step] — [Owner]

Be direct. No hedge language. Length: 300–450 words.
