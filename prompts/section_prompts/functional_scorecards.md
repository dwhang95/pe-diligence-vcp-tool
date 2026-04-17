You are a senior PE operations professional conducting functional due diligence on a buyout target.
Generate four structured functional scorecards based on the research and company context provided.
Each scorecard is a markdown table. Use only information available in the research summary and context notes.
When data is unavailable, say so explicitly and flag it as a diligence gap.

**Company:** {company_name}
**Industry:** {industry}
**EV Range:** {ev_range}
**Deal Type:** {deal_type}
**Description:** {description}
**Context Notes:** {context_notes}

**Research Intelligence:**
{research_summary}

---

## Instructions

For each scorecard, assess every dimension and assign a maturity rating:
- 🔴 **R** = High/Critical risk — impairs thesis or EBITDA if unaddressed
- 🟡 **Y** = Medium risk — needs diligence; mitigable with planning
- 🟢 **G** = Low risk — exists but unlikely to impair thesis

**100-Day Priority:** Y if material enough to address in the first 100 days post-close; N otherwise.
**Platform vs Tuck-In Impact:** Platform = affects the company as a standalone buy-and-build platform; Tuck-In = affects integration of add-on acquisitions; Both = affects both use cases.

When you lack data to assess a dimension, set Maturity to 🟡 Y and note "Insufficient data — assess in management meeting" in Current State Notes.

Keep Current State Notes tight: 1–2 sentences max. No generic filler. Be directional.

---

Output all four scorecards in sequence. Each ends with a **Key Outputs** block.

---

### Scorecard 1 — Operations

| Dimension | Assessment Area | Current State Notes | Maturity | 100-Day Priority | Platform vs Tuck-In Impact |
|---|---|---|---|---|---|
| Process Documentation | Are SOPs documented, current, and operationally embedded? | | | | |
| End-to-End Flow | Is the full ops flow (order-to-cash, procure-to-pay, etc.) mapped and understood? | | | | |
| Bottlenecks | Are production/service delivery bottlenecks identified and being actively managed? | | | | |
| Capacity Planning | Does the company have formal capacity planning against demand forecasts? | | | | |
| Cost Transparency | Is unit cost, overhead allocation, and margin by product/service visible? | | | | |
| Margin Leakage | Are pricing, scrap, returns, or rework creating untracked margin erosion? | | | | |
| Operating KPIs | Are operational KPIs defined, tracked, and visible to leadership weekly? | | | | |
| Continuous Improvement | Is there a culture and process for ongoing ops improvement (Lean, Kaizen, etc.)? | | | | |
| Vendor Management | Is the vendor base rationalized with contracts, SLAs, and performance tracking? | | | | |
| Quality Control | Are QC standards defined and defect/return rates tracked over time? | | | | |
| Customer Satisfaction | Is customer satisfaction measured (NPS, CSAT, complaint tracking) and acted upon? | | | | |
| M&A Readiness | Can the ops function absorb an add-on acquisition within 6–12 months? | | | | |
| Geographic Scalability | Could the operating model replicate in a new geography without major re-engineering? | | | | |
| Ops Leadership | Is there a capable, stable ops leader (COO/VP Ops) in seat? | | | | |
| Capital Intensity | Are capex requirements well-understood and in line with growth plans? | | | | |

**Key Outputs — Operations**

- **Top Risks:** [List the 2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [List the 2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what ops maturity means for EBITDA bridge and 100-day plan]

---

### Scorecard 2 — IT & Systems

| Dimension | Assessment Area | Current State Notes | Maturity | 100-Day Priority | Platform vs Tuck-In Impact |
|---|---|---|---|---|---|
| Core ERP | Is the ERP modern, well-implemented, and actively used across the business? | | | | |
| Financial Close | Is the monthly financial close timely (<10 days) and reliable? | | | | |
| Data Integrity | Is there a single source of truth for financial and operational data? | | | | |
| BI/Reporting | Does leadership have a real-time or near-real-time BI/reporting layer? | | | | |
| CRM Usage | Is CRM used consistently by the sales team with clean, actionable data? | | | | |
| Integrations | Are key systems (ERP, CRM, HRIS, etc.) integrated or siloed with manual bridges? | | | | |
| Scalability | Can current systems support 2x revenue growth without a full replacement? | | | | |
| M&A Readiness | Can the IT stack integrate an acquired company within 12–18 months? | | | | |
| IT Ownership | Is there a capable IT leader (CTO/IT Director) or is IT outsourced/underresourced? | | | | |
| Vendor Dependence | Is the company dangerously dependent on a single vendor or legacy system? | | | | |
| Tech Debt | Is there significant deferred IT investment creating operational risk? | | | | |
| Cybersecurity | Are basic cybersecurity controls in place (MFA, endpoint protection, incident response)? | | | | |
| Disaster Recovery | Is there a tested DR/BCP plan covering critical systems? | | | | |
| Access Controls | Are role-based access controls and separation of duties enforced? | | | | |
| Roadmap Clarity | Is there a documented IT roadmap aligned to business priorities? | | | | |

**Key Outputs — IT & Systems**

- **Top Risks:** [List the 2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [List the 2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what IT maturity means for the VCP and platform build thesis]

---

### Scorecard 3 — Commercial

| Dimension | Assessment Area | Current State Notes | Maturity | 100-Day Priority | Platform vs Tuck-In Impact |
|---|---|---|---|---|---|
| Growth Drivers | Are revenue growth drivers clearly identified and actively managed? | | | | |
| Sales Process | Is the sales process defined, repeatable, and consistently followed? | | | | |
| Sales Dependency | Is revenue overly dependent on the owner, a single rep, or a small team? | | | | |
| Pipeline Visibility | Is the sales pipeline visible, accurate, and used for forecasting? | | | | |
| Forecast Accuracy | Are revenue forecasts within ±10% variance to actuals on a rolling basis? | | | | |
| Lead Gen | Are lead generation channels diversified and performing predictably? | | | | |
| Pricing Discipline | Is pricing strategic, defensible, and enforced consistently? | | | | |
| Margin Visibility | Is gross margin tracked by customer, product line, and channel? | | | | |
| Retention | Is customer retention/churn tracked and above industry benchmarks? | | | | |
| Unit Economics | Are CAC, LTV, and payback period understood and healthy? | | | | |
| GTM Scalability | Can the go-to-market motion scale to new segments or geographies without major reinvestment? | | | | |
| Sales Enablement | Do reps have the tools, training, and collateral needed to close effectively? | | | | |
| Incentives | Are sales incentive structures aligned with margin, not just revenue? | | | | |
| Customer Concentration | Is revenue diversified, or does top-customer concentration create deal risk? | | | | |
| Cross-Sell/Upsell | Is there a proven motion to expand revenue within the existing customer base? | | | | |

**Key Outputs — Commercial**

- **Top Risks:** [List the 2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [List the 2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what commercial maturity means for the revenue growth thesis]

---

### Scorecard 4 — Talent & HR

| Dimension | Assessment Area | Current State Notes | Maturity | 100-Day Priority | Platform vs Tuck-In Impact |
|---|---|---|---|---|---|
| CEO Capability | Does the CEO have the capability and bandwidth to lead through PE ownership and growth? | | | | |
| CFO Capability | Does the CFO have PE-grade financial reporting, controls, and strategic finance capability? | | | | |
| COO Capability | Is there a capable operations leader who can own the VCP execution? | | | | |
| Leadership Bench | Is the broader leadership team (VPs, Directors) PE-ready and capable of scaling? | | | | |
| Retention | Are key employees being retained, and is attrition at or below industry norms? | | | | |
| Single Points of Failure | Are there individuals whose departure would materially impair operations or client relationships? | | | | |
| Hiring Velocity | Can the company hire fast enough to support the growth plan? | | | | |
| Org Design | Is the org structure aligned to the strategy, or are there gaps and misalignments? | | | | |
| M&A Experience | Has the leadership team managed through acquisitions or integrations before? | | | | |
| Incentive Alignment | Are equity/bonus structures aligned to PE value creation milestones? | | | | |
| Performance Mgmt | Is there a consistent, documented performance management process? | | | | |
| Culture | Is the company culture conducive to change, accountability, and PE ownership? | | | | |
| Succession Planning | Are successors identified for critical roles? | | | | |
| Talent Gaps | Are there open critical roles or known capability gaps that could impair the thesis? | | | | |

**Key Outputs — Talent & HR**

- **Top Risks:** [List the 2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [List the 2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what talent/HR maturity means for the 100-day plan and platform thesis]
