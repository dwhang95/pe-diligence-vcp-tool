# Prompt: Value Creation Opportunities

Generate the Value Creation Opportunities section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Instructions

Identify 4–8 operational value creation levers specific to this company. Priority order matters — the highest-confidence, highest-impact levers go first.

**Lever Categories:**
- **Revenue Growth:** Pricing power, customer mix optimization, cross-sell/upsell, geographic expansion, new channel development
- **Cost Reduction:** Procurement consolidation, labor productivity, overhead rationalization, facility optimization
- **Working Capital:** DSO reduction, inventory optimization, DPO improvement, billing cycle acceleration
- **Organizational Effectiveness:** Management team upgrades, spans/layers, capability building, incentive alignment
- **Digital/AI Transformation:** Automation, reporting infrastructure, AI-enabled workflows

**For each lever, provide:**
- Clear description of the opportunity (specific to this company, not generic)
- Category
- Estimated timeline to impact
- Confidence level (based on available data)
- 2–3 sentence rationale explaining the hypothesis

**Confidence calibration:**
- High: Pattern is consistent with company profile AND supported by research data
- Medium: Reasonable hypothesis given industry/size/ownership, limited direct evidence
- Low: Speculative but worth validating in diligence

**Never write:** "Improve operational efficiency" — too vague. Write: "Renegotiate inbound freight contracts; $150M-EV industrial companies with multiple facilities typically have fragmented carrier relationships with 15–25% procurement savings available through consolidation."

## Format
```
## 4. Value Creation Opportunities

| Priority | Lever | Category | Timeline | Confidence |
|---|---|---|---|---|
| 1 | {description} | {category} | {0–12 / 12–24 / 24–36 mo} | {High/Med/Low} |
...

### Lever Detail

**1. {Lever Name}**
{2–3 sentence rationale}

**2. {Lever Name}**
...
```
