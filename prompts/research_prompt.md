# Research Prompt — Company Intelligence Gathering

You are conducting pre-diligence research on a PE buyout target. Your goal is to gather operational intelligence that would inform a diligence brief.

## Company
- Name: {company_name}
- Description: {description}
- Industry: {industry}

## What to Search For

Run searches targeting the following categories of information:

### 1. Company Overview & News
- Recent press releases, news articles, announcements
- Ownership history (founder-led? Prior PE sponsors? How many?)
- Major customer wins or losses
- M&A activity (has the company acquired others? Been part of a roll-up?)

### 2. People & Culture Signals
- Glassdoor reviews (overall rating, management reviews, "cons" themes)
- LinkedIn: employee count growth/decline trends, leadership tenure, recent departures
- Any executive leadership changes in past 2 years

### 3. Operational Signals
- Facility locations and count
- Any expansion, closure, or relocation announcements
- Union activity or labor disputes
- Quality incidents, recalls, regulatory actions, lawsuits

### 4. Customer & Market Signals
- Named customers (often in case studies or press releases)
- Industry position (market leader? Niche player? Commoditized?)
- Industry headwinds or tailwinds

### 5. Technology Signals
- Job postings (what systems are they hiring for?)
- Any digital transformation announcements
- Tech stack signals from LinkedIn or job boards

## Output Format

Summarize findings in this structure:
```
### Research Findings: {company_name}

**Sources consulted:** [list URLs]

**Ownership & History**
{Findings}

**People & Culture**
{Findings — include Glassdoor rating if found}

**Operations**
{Findings}

**Customers & Market**
{Findings}

**Technology**
{Findings}

**Red Flags Identified**
{Any concerning signals found in research}

**Key Unknowns**
{What you couldn't find that matters}
```

If a category yields no useful information, state "No public data found — assess in diligence" and move on.
