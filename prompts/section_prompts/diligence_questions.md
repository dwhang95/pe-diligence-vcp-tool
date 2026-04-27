# Prompt: Key Diligence Questions

Generate the Key Diligence Questions section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Risk flags identified: {risk_flags_summary}
- Research findings: {research_summary}

## Instructions

Generate 10–15 operational diligence questions that a PE ops partner would want answered before IC or before the first management meeting.

These are questions for management — they should be:
- Specific enough that a vague answer is itself a data point
- Structured to surface problems, not confirm the investment thesis
- Prioritized: the most important questions come first

**Question themes to cover (select the most relevant for this company):**
- Management team depth and key-man dependency
- Customer relationships and contract structure
- Operational infrastructure and capacity
- IT systems and data quality
- Financial reporting and KPI visibility
- Supply chain and vendor dependencies
- Quality systems and compliance posture
- Workforce and labor dynamics
- Integration history (if bolt-on or acquisition history exists)
- Capital allocation and capex philosophy

**Good question format:** "Walk me through what happens when [key person] is out for two weeks — who owns [critical function] and what breaks?"

**Bad question format:** "What are your key operational challenges?" (too open, too easy to dodge)

Organize by theme with a theme header for each group of 2–3 questions.

## Format
```
## 6. Key Diligence Questions

### Management & Organization
1. {{Question}}
2. {{Question}}

### Customer & Revenue Quality
3. {{Question}}
4. {{Question}}

### Operations & Infrastructure
...
```
