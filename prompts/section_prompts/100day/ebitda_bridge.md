## Deal Context

{context_block}

---

## Task

Build a detailed EBITDA bridge for **{company_name}** from entry EBITDA of **${entry_ebitda:,.0f}K** to target EBITDA of **${target_ebitda:,.0f}K** — a required lift of **${ebitda_delta:,.0f}K ({ebitda_growth_pct}%)** over **{hold_period_years} years**.

**1. Bridge Components**
For each of the top value levers listed below, provide:
- Estimated EBITDA contribution ($K range — be honest about uncertainty)
- Primary driver (revenue growth, margin expansion, cost reduction, working capital — note: working capital affects cash, not EBITDA directly)
- Time to impact (Year 1 / Year 2 / Year 3+)
- Confidence level (High / Medium / Low) with one-line rationale
- Key dependency or risk that could impair realization

**Top Value Levers:**
{top_value_levers}

**2. Bridge Summary Table**
Present a markdown table: Lever | EBITDA Impact ($K) | Year | Confidence | Key Risk

**3. Gap Analysis**
- Sum the lever contributions. Does the math close to ${ebitda_delta:,.0f}K?
- If there is a gap, flag it explicitly and suggest what additional levers or assumptions would be needed
- Do not paper over a gap with optimism — flag it as a diligence risk

**4. Quick Wins vs. Structural Improvements**
- Categorize each lever: Quick Win (Days 30–60, low complexity) vs. Structural (requires systems, leadership, or process change)
- Quick wins should be visible AND impactful — not just easy

**5. Risks to the Bridge**
- Top 3 scenarios that could impair the bridge by >20%
- For each: probability assessment and mitigation

**Investment Thesis:**
{pe_thesis}

**Key Challenges:**
{key_challenges}

Be a senior operator, not an optimistic banker. If the bridge is aggressive, say so and explain what has to be true for it to work.

Format as structured markdown with numbered sections and the summary table in section 2.
