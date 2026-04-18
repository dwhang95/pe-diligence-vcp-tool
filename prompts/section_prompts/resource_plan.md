## Deal Context

{context_block}

---

## Task

Generate a 3rd party resource plan for **{company_name}**, a **{deal_type}** in **{industry}**.

Output a single markdown table with these exact columns:

| Workstream | Vendor Type | Typical Firm Examples | Scope | Engagement Timing | Estimated Cost Range | PE Sponsor Driven (Y/N) |
|---|---|---|---|---|---|---|

---

## Output Rules

**1. Include Only Genuine Vendor Needs**
Not every workstream requires outside help. Only include a row where 3rd party expertise is genuinely necessary — because the work requires independence, specialized capability, or bandwidth the portco team cannot provide in 100 days. If portco management can handle it internally, leave it out. A bloated vendor list signals poor ops judgment.

**2. Vendor Type — Be Specific**
Never write "consulting firm" or "vendor." Use precise categories:
- Big 4 accounting firm (QofE, tax structuring, audit readiness)
- Regional accounting firm (ongoing bookkeeping, local tax compliance)
- IT systems integrator — regional (ERP configuration, data migration <$5M project)
- IT systems integrator — national (ERP implementation $5M+, multi-site rollout)
- Executive search firm — generalist (CEO, CFO, COO)
- Executive search firm — functional specialist (CHRO, CRO, supply chain)
- HR/benefits broker (benefits plan design, carrier selection, 401k rollover)
- Insurance broker (D&O, E&O, workers' comp, property — post-close coverage)
- Commercial due diligence firm (customer interviews, market sizing, competitive analysis)
- Legal counsel — M&A/transactional (purchase agreement, reps & warranties, closing)
- Legal counsel — employment (offer letters, severance, non-competes)
- Legal counsel — regulatory/compliance (industry-specific: FDA, EPA, OSHA, etc.)
- Sell-side QofE firm (if carve-out financials need restatement)
- Restructuring advisor (if significant cost reduction or debt refinancing is in scope)
- IT security / cybersecurity firm (post-close assessment, penetration testing)
- Interim executive placement firm (fractional CFO, interim COO)
- Commercial real estate broker (lease renegotiation, facility consolidation)
- Environmental consultant (Phase I/II ESA, if real property involved)
- Supply chain / procurement consultant (if sourcing optimization is a top value lever)

Add others as appropriate to the deal type and industry. Never invent vague categories.

**3. Typical Firm Examples**
Name 2–3 real, recognizable firms per vendor type. Do not use placeholder names. Use firms that actually operate in PE portco engagements at the middle market scale ($50M–$500M EV). Examples by category:
- Big 4: Deloitte, PwC, EY, KPMG
- Regional accounting: BDO, Grant Thornton, RSM, Plante Moran
- IT integrator (regional): Sikich, Plante Moran, Wipfli
- IT integrator (national): Accenture, Cognizant, Infosys, Wipro
- Executive search (generalist): Spencer Stuart, Korn Ferry, Heidrick & Struggles
- Executive search (functional): StevenDouglas, Caldwell, Stanton Chase
- HR/benefits broker: Mercer, Willis Towers Watson, Gallagher, NFP
- Insurance broker: Marsh, Aon, Lockton, USI
- Commercial DD: AlixPartners, L.E.K., FTI Consulting, Bain (commercial)
- Legal (M&A): Kirkland & Ellis, Ropes & Gray, Latham & Watkins, Paul Weiss
- Legal (employment): Littler Mendelson, Fisher Phillips, Ogletree Deakins
- Cybersecurity: Mandiant, CrowdStrike, NCC Group, Stroz Friedberg

**4. Cost Ranges — Middle Market Reality**
Use realistic PE portco ranges for $50M–$500M EV deals. Do not use enterprise pricing. Do not lowball to look conservative. Examples:
- QofE (Big 4, full scope): $150K–$400K
- QofE (regional, limited scope): $75K–$150K
- ERP implementation (mid-market, e.g. NetSuite, Sage Intacct): $250K–$800K
- ERP implementation (Tier 1, e.g. SAP, Oracle): $1M–$4M
- Executive search (C-suite): $80K–$150K per role (typically 25–30% of Year 1 comp)
- Interim CFO (fractional, 3–6 months): $15K–$30K/month
- HR/benefits migration: $20K–$60K
- D&O insurance (post-close): $50K–$200K/year
- Cybersecurity assessment: $40K–$120K
- Employment legal (post-close, standard): $25K–$75K
- Commercial real estate broker: typically success-fee only, $0 out-of-pocket
- Environmental consultant (Phase I): $3K–$8K per site

Adjust ranges for deal complexity, company size, and industry. Flag wide ranges with a note in Scope.

**5. Deal Type Adjustments**
Certain vendor categories are mandatory or should be emphasized by deal type:

**Carve-out:** Must include QofE/financial restatement, TSA advisory (Big 4 or AlixPartners), legal for entity separation, HR/benefits migration broker, and likely IT integrator for standalone systems standup.

**Platform:** Must include executive search if management gaps were flagged, reporting/BI implementation partner, and typically D&O/insurance broker for new board coverage.

**Tuck-in:** Must include legal for integration (employment, contracts novation), HR/benefits if combining plans, and IT integrator if systems consolidation is in scope.

**6. PE Sponsor Driven (Y/N)**
- **Y** — the PE sponsor typically selects, contracts, and manages this vendor directly (e.g., QofE firm, M&A legal, D&O insurance, commercial DD)
- **N** — portco management owns the vendor relationship with PE sponsor oversight (e.g., ERP implementation, HR/benefits broker, supply chain consultant)
- Use Y/N only. Do not write "Shared" — pick the primary driver.

---

## After the Table

Add a **"Total Estimated 3rd Party Spend"** section immediately after the table.

Format it as:

### Total Estimated 3rd Party Spend — 100-Day Window

| Category | Low Estimate | High Estimate |
|---|---|---|
| [Vendor Type 1] | $XXK | $XXK |
| [Vendor Type 2] | $XXK | $XXK |
| ... | | |
| **Total** | **$XXXk** | **$X.XM** |

Then add 2–3 sentences of plain-language commentary: what's driving the range, which single engagement has the most cost variance, and whether the total is typical or elevated for this deal type.

---

## Tone

Direct, not defensive. A PE ops professional reviewing this table should be able to immediately tell whether the vendor selection is appropriate for the deal — not whether it's exhaustive. If a category is excluded, that's a judgment call, not an oversight. Write vendor scope descriptions in active voice: "Conducts QofE on trailing 24 months of financials" not "Quality of earnings work will be performed."
