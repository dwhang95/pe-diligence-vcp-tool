# Prompt: Credit & Financial Metrics

Generate the Credit & Financial Metrics section for the PE ops diligence brief.
This section applies to Financial Services and Fintech companies.

## Input Context
- Company: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Context notes: {context_notes}
- Research findings: {research_summary}

## Instructions

Assess credit quality, financial structure, and regulatory position. This section informs IC on underwriting risk and business model durability — not just the income statement.

**1. Loss Curves & Credit Performance**
- Estimated charge-off rates vs. industry benchmarks (state the benchmark explicitly)
- Is vintage performance improving or deteriorating? What does the trajectory imply?
- Key metrics to request from management: 30/60/90 day DPD rates, net charge-off rate by vintage, recovery rates
Flag if the book is too young or growing too fast to assess loss curves reliably.

**2. Net Interest Margin (NIM)**
- Estimated or reported NIM vs. comparable lenders or fintech peers
- Funding cost structure and sensitivity to rate changes (rising vs. falling rate environment)
- NIM compression risk: is the spread durable if rates normalize or if competition intensifies?

**3. Funding Stack**
- How is the portfolio funded? (deposits, warehouse lines, securitization facilities, equity)
- Concentration risk in funding sources — single-lender facility is a critical dependency
- Refinancing risk: when do key facilities expire? Is rollover risk hedged by relationship or terms?

**4. Regulatory Trajectory**
- Applicable regulatory regime: CFPB, OCC, state banking/lending laws, FinCEN, FINRA (as relevant)
- Any known enforcement actions, consent orders, or regulatory correspondence in the last 3 years
- Tail risk: rate cap legislation, BNPL regulation, open banking mandates, or other regulatory changes that could impair the business model
Note what the company's regulatory posture has been: proactive vs. reactive.

**5. Vintage Analysis Sufficiency**
- Is there enough seasoned data to assess portfolio quality at IC?
- Flag new or rapidly growing books: they look clean until 12–24 months of seasoning
- Minimum data requirements before IC: define the specific cohort vintage periods and loss curve depth needed

## Format

Lead with a one-line credit quality characterization (e.g., "Credit performance appears adequate at current scale but insufficient data exists to assess durability through a cycle.").
Write as flowing analysis with bolded sub-headers.
Flag critical unknowns explicitly — state what management must provide and why it is material.
Length: 400–550 words.
