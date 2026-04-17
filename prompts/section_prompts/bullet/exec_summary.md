# Prompt: Executive Summary (Bullet Mode)

Generate the Executive Summary section for the PE ops diligence brief.

## Input Context
- Company name: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- 2 lines of prose intro maximum. Then bullets only. No paragraphs after that.
- Every bullet maximum 25 words. Cut ruthlessly.
- Do not restate context already in the input.
- No hedging language ("it appears", "it seems", "may potentially").
- State the finding, then the implication. Nothing else.
- 200 words MAXIMUM for the entire section.

## Instructions

Write exactly 2 lines of intro (operational snapshot: what they do, how they make money). Then exactly 5 bullets:
1. Operational profile — classification + one implication
2. Labor intensity (High/Med/Low) + one implication
3. Tech dependency (High/Med/Low) + one implication
4. Overall Ops Risk Rating (Low / Medium / High / Critical) + 1-line justification
5. Single biggest open question diligence must resolve

## Format
```
## 1. Executive Summary

{Line 1: what the company does, operational lens.}
{Line 2: how they make money and key ops characteristic.}

- **Operational Profile:** {classification} — {one implication, max 15 words}
- **Labor Intensity:** {High/Medium/Low} — {one implication, max 15 words}
- **Tech Dependency:** {High/Medium/Low} — {one implication, max 15 words}
- **Overall Ops Risk: {Low/Medium/High/Critical}** — {1-line justification, max 20 words}
- **Key Open Question:** {the single most important thing diligence must resolve, max 20 words}
```
