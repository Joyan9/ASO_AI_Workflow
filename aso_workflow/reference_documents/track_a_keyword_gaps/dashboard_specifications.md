# Track A: Keyword Gap Analysis Report — HTML Specification

Single self-contained HTML file. All data embedded as JS variables. No external dependencies
at runtime except CDN links below.

---

## Tech Stack

```html
<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

<!-- Charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

## Design Tokens

```css
:root {
  --bg-page:        #0f1117;
  --bg-card:        #1a1d27;
  --bg-card-alt:    #1f2235;
  --border:         #2a2d3e;
  --accent:         #6c63ff;
  --accent-soft:    rgba(108, 99, 255, 0.15);
  --accent-2:       #00d4a8;
  --accent-2-soft:  rgba(0, 212, 168, 0.12);
  --warn:           #f59e0b;
  --text-primary:   #f0f0f5;
  --text-secondary: #8b8fa8;
  --text-mono:      #a8b2d8;
  --tier1-border:   #6c63ff;
  --tier2-border:   #00d4a8;
  --tier3-border:   #f59e0b;
  --font-sans:      'Space Grotesk', sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
}
```

---

## Page Structure

```
<nav>           Fixed left sidebar, 220px wide, section anchors
<main>          margin-left: 220px, max-width: 1200px
  #hero         App name, run metadata, scope pills
  #summary      Executive summary + 5 recommendation cards
  #gap-chart    Horizontal bar chart + full sortable table
  #longtail     Long-tail & low-signal table
  #landscape    Competitive landscape table
</main>
```

---

## Navigation Sidebar

Fixed left, full height, dark background (`--bg-card`), border-right `--border`.

Links: Executive Summary · Keyword Gaps · Long-tail · Competitive Landscape

Active section highlighted with `--accent` left border and text. Smooth scroll on click.

At top of sidebar: app name in mono font, platform badge (iOS / Android pill).

---

## Section 1: Hero

Full-width dark bar (`--bg-page`). Two rows:

**Row 1:** App name (Space Grotesk 700 32px) + platform badge pill

**Row 2:** Metadata pills in a flex row — each pill is a small rounded badge (`--bg-card`, `--border`):
- `📅 Run date: {date}`
- `🌍 Country: {country}`
- `🔍 Seeds generated: {n}`
- `✅ Seeds with data: {n}`
- `🎯 Gap terms (filtered): {n}`

Below pills: assumptions as a collapsed `<details>` block, closed by default. Label: "Analysis assumptions ▾"

---

## Section 2: Executive Summary + Recommendations

### 2a. Executive Summary

Card (`--bg-card`, border-left 3px `--accent`). 3–4 sentence paragraph. Mono font for any
term or number cited inline.

### 2b. Recommendation Cards

5 cards in a grid (2 columns on desktop, 1 on mobile). Each card:

```
┌─────────────────────────────────┐
│ 01              [category pill] │  ← number in accent colour, pill = type label
│                                 │
│ Headline (700 18px)             │
│                                 │
│ Rationale text (secondary)      │
│                                 │
│ ▶ Action text (accent colour)   │
└─────────────────────────────────┘
```

Card background: `--bg-card`. Border-top: 3px `--accent`. Hover: border-top `--accent-2`,
subtle background shift to `--bg-card-alt`.

Category pill colours by type:
- Priority gap → `--accent`
- Quick win → `--accent-2`
- Long-tail → `--warn`
- iOS keyword field → `#e879f9`
- Category trend → `#38bdf8`

---

## Section 3: Keyword Gap Table

### 3a. Bar Chart

Horizontal bar chart (Chart.js). Y-axis: top 20 gap terms by avg KEI. Stacked bars:
- Primary competitor count → `--accent`
- Secondary competitor count → `--accent-soft` with `--accent` border

Chart height: 480px. Dark background, no gridlines except subtle vertical ones.
Chart title: "Top 20 gap terms by competitor coverage".

### 3b. Table Controls

Row between chart and table:
- Left: `Filter: [_________]` text input (filters table rows live by term substring)
- Right: `Export CSV` button (outlined, `--accent` border, triggers client-side download)

### 3c. Gap Table

Columns: Term | Volume | Difficulty | Top rank | Avg installs | Avg KEI | Primary | Secondary | Apps using it | Fields

- Term column: `--font-mono`, slightly larger
- Volume / Difficulty / KEI / rank: right-aligned, mono font
- `—` for null values, coloured `--text-secondary`
- Apps using it: comma-separated app names, truncated to 30 chars with tooltip for full list
- Rows where all 3 primary competitors rank: left border 3px `--tier1-border`, background `--accent-soft`
- Default sort: primary DESC, avg KEI DESC
- Clicking column header sorts ascending/descending; active sort column header shows ▲/▼

Table style: `--bg-card`, rows alternate between `--bg-card` and `--bg-card-alt`, border-bottom
`--border` on each row. No outer border.

---

## Section 4: Long-tail & Low-signal

Section header: "Long-tail & Low-signal Opportunities" + subtitle in secondary colour.

Narrative paragraph (from LLM) above the table.

Table columns: Term | Primary count | Secondary count | Apps ranking (names)

- Term: mono font
- Export CSV button top-right

Same row styling as section 3 but no chart.

---

## Section 5: Competitive Landscape

Section header: "Competitive Landscape"

Narrative paragraph (2–3 sentences from LLM) above the table.

Table columns: Competitor | Tier | Unique gap terms they rank for

- Tier: pill badge — Primary (`--accent-soft`, `--accent` text), Secondary (`--bg-card-alt`,
  `--text-secondary`)
- Unique gap terms: right-aligned, mono font, coloured `--accent` for primary rows
- Sort by tier first, then gap term count DESC

No chart in this section.

---

## Data Embedding Pattern

All report data must be embedded at the top of the `<script>` block:

```javascript
const REPORT_DATA = { /* full JSON pasted here */ };
```

All chart data, table rows, and dynamic text must be derived from `REPORT_DATA` in JS.
Do not hardcode any terms, names, or numbers directly into HTML.

---

## CSV Export

Each table has its own export button. On click, generate a CSV from the table's current
filtered/sorted state (not the original data). Filename pattern:

- Gap table: `keyword_gaps_{platform}_{app_id}_{date}.csv`
- Long-tail table: `longtail_{platform}_{app_id}_{date}.csv`

Use client-side `Blob` + `URL.createObjectURL` — no server required.

---

## Responsiveness

- Sidebar collapses to top nav bar below 768px
- Grid goes to 1 column below 768px
- Tables get horizontal scroll wrapper below 768px, no content truncation
- Chart height reduces to 320px on mobile

---

## Typography Scale

| Use | Font | Size | Weight |
|---|---|---|---|
| App name | Space Grotesk | 32px | 700 |
| Section headers | Space Grotesk | 22px | 700 |
| Card headlines | Space Grotesk | 18px | 700 |
| Body / narrative | Space Grotesk | 15px | 400 |
| Table body | Space Grotesk | 14px | 400 |
| Terms / numbers | JetBrains Mono | 13px | 400 |
| Pills / badges | Space Grotesk | 11px | 500 |