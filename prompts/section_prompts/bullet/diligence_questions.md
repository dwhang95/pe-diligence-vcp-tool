# Prompt: Key Diligence Questions (Bullet Mode)

Generate the Key Diligence Questions section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Risk flags identified: {risk_flags_summary}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- Maximum 10 questions. Each = exactly 1 line.
- No theme headers, no sub-bullets, no explanations.
- Questions must be specific enough that a vague answer is itself a data point.
- Do not restate context already in the input.
- Prioritized: most important first.

## Instructions

Generate the 10 most important operational diligence questions for management. Questions must be specific to this company and structured to surface problems, not confirm the thesis.

Cover the highest-priority themes from: management depth / key-man, customer relationships / contracts, operational infrastructure, IT systems / data, supply chain / vendor dependencies, workforce dynamics.

## Format
```
## 6. Key Diligence Questions

1. {{Question — specific, 1 line, max 30 words}}
2. {{Question — specific, 1 line, max 30 words}}
3. {{Question — specific, 1 line, max 30 words}}
4. {{Question — specific, 1 line, max 30 words}}
5. {{Question — specific, 1 line, max 30 words}}
6. {{Question — specific, 1 line, max 30 words}}
7. {{Question — specific, 1 line, max 30 words}}
8. {{Question — specific, 1 line, max 30 words}}
9. {{Question — specific, 1 line, max 30 words}}
10. {{Question — specific, 1 line, max 30 words}}
```
