# Prompt: 100-Day Plan Outline Starter (Bullet Mode)

Generate the 100-Day Plan Outline section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Risk flags identified: {risk_flags_summary}
- Value creation levers identified: {vc_levers_summary}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- Maximum 3 workstreams per phase. Each = exactly 1 bullet.
- Every bullet maximum 25 words.
- Bullets must reference specific risks/levers from this company — not generic templates.
- No hedging language. No prose paragraphs.
- Do not restate context already in the input.

## Instructions

Three non-negotiable principles (reflect in the plan, don't state them as bullets):
1. Days 1–30 are for listening, not fixing.
2. Quick wins (Days 30–60) must be visible AND impactful.
3. Board reporting cadence established by Day 60.

Each phase: max 3 bullets, each referencing actual risks or levers identified above.

## Format
```
## 5. 100-Day Plan Outline Starter

### Days 1–30: Listen & Diagnose
- {Specific listening/diagnostic action tied to this company — max 25 words}
- {Specific listening/diagnostic action tied to this company — max 25 words}
- {Specific listening/diagnostic action tied to this company — max 25 words}

### Days 31–60: Align & Quick Wins
- {Specific workstream or quick win tied to a lever or risk — max 25 words}
- {Specific workstream or quick win tied to a lever or risk — max 25 words}
- {Governance/reporting setup action — max 25 words}

### Days 61–100: Execute & Report
- {First deliverable from priority workstream — max 25 words}
- {KPI baseline or board reporting action — max 25 words}
- {Year 1 plan handoff or transition action — max 25 words}
```
