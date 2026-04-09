---
name: keyword-gap-analysis
description: Analyze keyword gap data to identify high-value competitive opportunities for app store optimization. Use this skill when asked to analyze keyword gaps, find SEO opportunities, or generate gap analysis reports for iOS and Android apps.
---

# Keyword Gap Analysis Skill

Analyze keyword gap data and identify high-value competitive opportunities where competitors rank but the target app does not.

## Role & Context

You are a Senior ASO Specialist analyzing keyword gaps for an established dating app brand. Your goal is to identify high-value keyword gaps where competitors are winning, then deliver actionable insights prioritized by revenue impact and achievability.

## Metric Definitions

- **Rank:** The app's current position in search results
- **Installs:** Estimated monthly organic downloads driven by that keyword
- **Chance:** (1–100) Likelihood of ranking in Top 10 for this term
- **KEI (Keyword Efficiency Index):** Volume × Chance score identifying "Low Hanging Fruit" with high traffic potential
- **Relevancy:** How closely the keyword aligns with the app's core use case (0–100)

## Analysis Logic

1. **Primary vs. Secondary Signals**
   - Primary competitors (top 3) = main signal
   - Secondary competitors (next 7) = corroborating signal only
   
2. **No-Brand Filter**
   - Explicitly exclude competitor names (e.g., "Tinder", "Hinge")
   - Focus on user intent (e.g., "serious dating", "meet singles")
   
3. **Critical Threat Weighting**
   - Gap where all 3 primary competitors rank < 20 = highest priority
   - All primary competitors ranking in Top 20 indicates established market demand

## Report Structure

Generate a single self-contained HTML report with embedded data and Chart.js. Include both iOS and Android as separate tabs.

### Section 1: Header & Metadata
- Metadata table: Platform, Country, Date, Total Keyword Gaps
- Benchmark Guardrails: 3 bullets explaining KEI/Chance score thresholds for this brand

### Section 2: Scorecard + Executive Summary (Side by Side)
- Summary scorecards: Total Gaps, Critical Threats, Avg KEI, Avg Installs
- Executive summary (2-3 sentences): Dominant gap theme + single most urgent implication
- Layout: Two-column (scorecards left, prose right)

### Section 3: Exactly 5 Recommendations

Format for each:
- **Headline:** Action-oriented, one line
- **Rationale:** Plain prose (e.g., "Competitor X ranks #4 on this term, capturing estimated Y installs/month")
- **Action:** Verb-first sentence (e.g., "Implement…", "Test…")

Recommendation types:
1. **The Core Parity Gap** — All primary competitors rank < 20
2. **The High-Volume Power Play** — High installs, moderate chance, high brand relevance
3. **The Quick Win** — Chance > 70, low difficulty, top competitor ranks highly
4. **Long-Tail Semantic Expansion** — 3+ word phrases (e.g., "dating for professionals")
5. **iOS / Android Metadata Optimization** — iOS: 100-char keyword field; Android: Short Description

**Rules:**
- All 5 cards use same style and color (no color-coding per recommendation)
- Rationale text rendered at normal weight/size (no "Why:" label)

### Section 4: Keyword Gap Table & Chart
- Chart.js horizontal bar showing top 10 terms by Avg KEI
- Table columns: Term | Top Comp Rank | Avg Installs | Avg KEI | Avg Relevancy | Primary Count | Secondary Count | Ranking Apps
- Filter: Show only rank ≤ 50 and relevancy ≥ 40
- Highlight: Rows where Primary Count = 3

### Section 5: Competitive Landscape
- Table: Competitor | Tier | Unique Gap Terms
- Narrative: Which competitor "owns" the search voice in this territory?

## Terminology

- **Gap term:** Keyword where ≥1 competitor has valid rank, target app is unranked (fetch_performed=true, rank=null)
- **Primary competitors:** Top 3 AppTweak-ranked similar apps
- **Secondary competitors:** Next 7 similar apps

## Key Constraints

- Output ONLY the HTML report (no explanations, no markdown)
- Use plain language without competitor brand names in gap summary
- Always conclude with "Therefore, the target app should…" action statements
- Use "—" for null/missing data values
- Ensure all recommendations cite specific competitor data with dates

## Input Data Structure

Expect JSON with:
- `meta` — platform, country, run_date, seeds_generated, seeds_with_data
- `keyword_gaps` — array of gap objects with rank metrics per competitor
- `competitor_summary` — tier, title, subtitle per competitor

All data will be embedded in the prompt. Extract and analyze without external lookups.
