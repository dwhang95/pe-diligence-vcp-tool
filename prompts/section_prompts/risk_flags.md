# Prompt: Operational Risk Flags

Generate the Operational Risk Flags section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Deal type: {deal_type}
- Description: {description}
- Research findings: {research_summary}

## Instructions

Assess each of the 5 risk categories below. For each:
1. Provide a directional hypothesis (1–3 sentences) — what do you suspect and why?
2. Assign a risk level: **Low / Medium / High / Critical**
3. Provide 1–2 specific diligence questions to validate or refute your hypothesis

**Risk Categories:**

### A. People & Organization
Focus on: key-man dependency, management team depth, union exposure, retention signals (Glassdoor if available, turnover proxies), bench strength below CEO/COO level.

Middle market rule of thumb: founder-led companies almost always have key-man risk. PE-backed companies with 2+ sponsors often have management fatigue.

### B. Operational Infrastructure
Focus on: facility conditions (# of sites, ownership vs. lease, age signals), capacity utilization hypothesis, capex overhang (has maintenance capex been deferred?), scalability of current ops model.

### C. Supply Chain & Procurement
Focus on: input cost exposure (commoditized inputs = margin vulnerability), vendor concentration, geographic sourcing risk, inventory management signals.

### D. Quality & Compliance
Focus on: regulatory environment for this industry (FDA, OSHA, EPA, state licensing), certification requirements (ISO, AS9100, etc.), customer quality mandates, any public compliance history.

### E. Customer Concentration
Focus on: top customer dependency (>20% = flag, >40% = high risk), contract structure hypothesis (spot vs. long-term), end-market diversity, churn signals.

## Format
```
## 2. Operational Risk Flags

### A. People & Organization — {{Risk Level}}
{{Hypothesis}}

**Diligence questions:**
- {{Question 1}}
- {{Question 2}}

### B. Operational Infrastructure — {{Risk Level}}
...
```
