# Prompt: Executive Summary

Generate the Executive Summary section for the PE ops diligence brief.

## Input Context
- Company name: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Deal type: {deal_type}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Instructions

Write a 3–5 sentence operational snapshot of the company. Focus on:
1. What they do and how they make money (operational lens, not financial)
2. Operational profile classification — choose the most accurate:
   - Asset-heavy / capital-intensive (manufacturing, logistics, facilities-dependent)
   - Asset-light / people-intensive (professional services, staffing, care delivery)
   - Tech-enabled / platform (SaaS, marketplace, digital-native)
   - Hybrid (asset-light at corporate, heavy at site level)
3. Labor intensity (high / medium / low) and what that implies for ops
4. Technology dependency (core to value delivery vs. back-office only)

Then assign an **Overall Ops Risk Rating**: Low / Medium / High / Critical

Justify the rating in 1–2 sentences. Be direct. Don't hedge.

## Format
```
## 1. Executive Summary

{{3–5 sentence snapshot}}

**Operational Profile:** {classification}
**Labor Intensity:** {{High/Medium/Low}} — {{one-line implication}}
**Tech Dependency:** {{High/Medium/Low}} — {{one-line implication}}

**Overall Ops Risk Rating: {{Low/Medium/High/Critical}}**
{{1–2 sentence justification}}
```
