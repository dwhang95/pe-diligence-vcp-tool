# Prompt: SaaS & Technology Metrics

Generate the SaaS & Technology Metrics section for the PE ops diligence brief.
This section applies to Technology and SaaS companies.

## Input Context
- Company: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Instructions

Assess business model quality, growth health, and technology moat. The goal is to separate durable SaaS economics from cyclical or fragile revenue.

**1. Revenue Quality — ARR / MRR Profile**
- Estimated ARR range and trajectory (growing, stable, declining?)
- Revenue composition: subscription vs. professional services vs. usage-based
- Stickiness indicators: multi-year contracts, product integrations, switching costs
If no public ARR data: state what the disclosure package must include and what typical ARR composition looks like for this company type.

**2. Net Revenue Retention (NRR)**
- Estimated NRR and what it implies for growth quality
- Benchmarks: SMB SaaS (<100% NRR is common but concerning); mid-market (100–110% is healthy); enterprise (>115% is strong, >120% is excellent)
- Expansion drivers: seat-based, usage-based, upsell? Which driver is most realistic for this company?
- Gross logo churn vs. net revenue churn distinction — which is more relevant here?

**3. CAC / LTV Economics**
- Customer acquisition model: direct sales, product-led growth (PLG), or channel?
- LTV/CAC ratio and payback period estimate — state the assumption basis
- Sales efficiency signal: ARR growth relative to S&M investment
Flag if the company has not yet reached LTV/CAC efficiency or is in a deliberate land-and-expand mode.

**4. Churn Analysis**
- Logo churn rate estimate vs. benchmarks
- Key churn drivers: pricing, competitive alternatives, product gaps, customer success under-investment
- Cohort risk: how much ARR is concentrated in accounts that are 3+ years old? What happens to NRR if these anchor accounts churn?

**5. Technology Moat Assessment**
- Point solution vs. platform: platform businesses have stronger NRR and are harder to displace
- Competitive replaceability: how easily can customers migrate to an alternative?
- Technical debt and infrastructure health: cloud-native vs. legacy, age of core codebase, any known refactoring backlog
- Key engineering talent dependencies — who built the product and are they still there?

## Format

Lead with a one-line business model quality characterization (e.g., "ARR appears healthy at current scale but NRR trajectory is the critical unknown before IC.").
Write as flowing analysis with bolded sub-headers.
Include benchmark context inline for each key metric.
Flag critical unknowns and specify the exact data to request.
Length: 400–550 words.
