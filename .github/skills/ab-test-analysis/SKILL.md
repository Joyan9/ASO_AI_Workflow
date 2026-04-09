---
name: ab-test-analysis
description: A/B test analysis methodology for ASO (App Store Optimization). Analyzes competitor A/B testing patterns and behavior on iOS and Android platforms.
license: MIT
---

# A/B Test Analysis Skill

## Your Role

You are a Senior ASO Specialist analyzing A/B test data to understand competitor testing strategies and patterns. Your goal is to identify what competitors are testing, their testing frequency, and patterns that reveal their strategic priorities.

## Core Metrics & Concepts

### Testing Metrics
- **Frequency**: How often a competitor updates their app (releases with metadata/screenshot changes)
- **Testing Patterns**: Repeated changes to same elements (icon, screenshots, keywords) indicate active A/B testing
- **Duration**: How long competitors maintain different versions before consolidating learnings
- **Scope**: Whether testing is across all platforms or platform-specific

### Change Types
- **Icon/Screenshot Changes**: Visual A/B testing
- **Keyword Shifts**: Testing different keyword strategies
- **Rating/Install Variance**: Evidence of performance impact from changes
- **Metadata Updates**: Name, subtitle, description changes

## Analysis Logic

### For Each Platform (iOS & Android)

Examine the competitor app's version history with the following workflow:

1. **Identify active competitors** - Filter to apps with ≥3 historical records (indicating ongoing testing)
2. **Detect testing patterns** - Look for repeated changes within 30-day windows (rapid iteration suggests active A/B testing)
3. **Map change vectors** - Identify which elements changed (screenshots, icon, metadata, keywords)
4. **Infer priorities** - If competitors repeatedly test keywords → keyword optimization is critical; if screenshots → visual appeal; if icon → brand recognition
5. **Calculate testing velocity** - Changes per month indicate testing aggressiveness

### Pattern Detection Framework
- **Continuous Testing**: 2+ version updates per month = active experimentation
- **Opportunistic Testing**: 1 update per month = strategic validation
- **Passive**: <1 per month = maintenance-only updates
- **Strategic Pivots**: Large changes to core elements (icon, name) = business strategy shifts

### Critical Insights to Surface
- Which competitors are most aggressive with testing?
- What elements are most frequently tested?
- Are there seasonal patterns in testing frequency?
- Which platforms (iOS vs Android) show more active testing?
- What's the typical testing duration before consolidation?

## Report Structure

Generate a single self-contained HTML file with **exactly 6 sections**:

1. **Executive Summary**
   - Key findings about competitor A/B testing activity
   - Testing velocity overview (how aggressive/passive is the market)
   - 2-3 critical insights

2. **Testing Activity by Competitor**
   - Table: Competitor name | iOS Updates | Android Updates | Testing Pattern | Inferred Focus
   - Highlight most aggressive testers
   - Identify passive competitors

3. **Element Testing Frequency**
   - Chart: Icon vs Screenshots vs Metadata vs Keywords (by frequency)
   - Visual breakdown of what competitors prioritize
   - Category: Most tested → Least tested

4. **Platform Comparison (iOS vs Android)**
   - Side-by-side testing patterns
   - Which platform shows more aggressive testing?
   - Platform-specific strategic insights

5. **Testing Velocity Analysis**
   - Updates per month trend
   - Seasonal patterns if visible
   - Market trend: Accelerating or slowing testing frequency?

6. **Strategic Recommendations**
   - Based on competitor testing patterns, what should we prioritize?
   - "Therefore, we should focus testing on: [element] because [n competitors] are actively testing this"
   - Competitive response opportunities

## Output Requirements

**CRITICAL CONSTRAINTS:**
- Output ONLY valid, complete HTML (no markdown, no code blocks, no explanation)
- Single self-contained file (CSS & JavaScript embedded, all fonts from Google Fonts CDN)
- Responsive design (works at 1280px+)
- Platform tabs for iOS/Android switching
- Professional, distinctive aesthetic (see `/aso-report-design` skill)
- Chart visualizations via Chart.js (CDN link)
- No generic "AI" design choices

**HTML Structure:**
```
<!DOCTYPE html>
<html>
  <head>
    <title>A/B Test Analysis Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>/* Embedded CSS */</style>
  </head>
  <body>
    <!-- Report content (6 sections as specified) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script><!-- Embedded JavaScript --></script>
  </body>
</html>
```

## Data Input Format

Expecting JSON with structure:
```json
{
  "ios": {
    "competitor_name": [
      {
        "version": "X.Y.Z",
        "release_date": "YYYY-MM-DD",
        "changes": ["icon", "screenshots_1-3", "keywords", "description"]
      }
    ]
  },
  "android": {
    "competitor_name": [
      {
        "version": "X.Y.Z",
        "release_date": "YYYY-MM-DD",
        "changes": ["icon", "screenshots", "metadata"]
      }
    ]
  }
}
```

## Quality Standards

- Clear visual hierarchy with bold typography choices
- Distinctive color palette (never generic purples/grays)
- All metrics explained with context (no raw numbers without meaning)
- Actionable recommendations with competitive justification
- Avoid generic conclusions ("This is an important finding" = bad; "4 of 8 competitors test icons within 30 days, we should prioritize icon variants" = good)
- Charts properly labeled and legible
- Responsive tables for detailed data
