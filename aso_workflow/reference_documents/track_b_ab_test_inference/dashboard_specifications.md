# A/B Test & Strategy Intelligence — HTML Specification

Single self-contained HTML file. All data embedded as JS variables. Chart.js via CDN.

---

## Tech Stack

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

## Design Tokens

Reuse the same tokens as Track A:

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
  --pending:        #f59e0b;
  --won:            #00d4a8;
  --lost:           #ef4444;
  --text-primary:   #f0f0f5;
  --text-secondary: #8b8fa8;
  --font-sans:      'Space Grotesk', sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
}
```

---

## Page Structure

```
<nav>     Fixed left sidebar, 220px, section anchors
<main>    margin-left: 220px, max-width: 1200px
  #hero
  #summary       Executive summary + recommendation cards
  #activity      Competitor activity table
  #tests         Test detail cards per competitor
  #signals       Cross-competitor signals (conditional)
</main>
```

---

## Navigation Sidebar

Same pattern as Track A. Links: Summary · Activity · Test Details · Signals

Top of sidebar: app name (mono), "Track B · Android" pill.

---

## Section 1: Hero

App name + "A/B Intelligence" label. Metadata pills:
- Run date | Country | History window | Competitors analysed | Total A/B tests | All pending pill (if applicable)

Collapsed "Analysis Scope" details block.

---

## Section 2: Executive Summary + Recommendations

### 2a. Executive Summary
Card with left border `--accent`. 3–4 sentence paragraph.

### 2b. Recommendation Cards

3–5 cards, 2-column grid. Same structure as Track A cards:

```
┌─────────────────────────────────┐
│ 01              [category pill] │
│                                 │
│ Headline (700 18px)             │
│                                 │
│ Evidence text (secondary)       │
│                                 │
│ ▶ Implication (accent)          │
└─────────────────────────────────┘
```

Category pill colours:
- Positioning shift → `--accent`
- Active test      → `--warn`
- Screenshot CRO   → `#38bdf8`
- Convergence      → `--accent-2`
- Testing gap      → `#e879f9`

---

## Section 3: Competitor Activity Table

Columns: Competitor | Tier | Fields tested | Total tests | Pending | Won | Lost | Last activity

- Tier: pill badge — Primary (`--accent-soft`), Secondary (`--bg-card-alt`)
- Won/Lost/Pending: coloured numbers (`--won`, `--lost`, `--pending`)
- Primary rows with title/short_description tests: left border 3px `--accent`
- Sort: primary first, total tests DESC
- No chart needed in this section

Bar chart above the table: horizontal bars, one per competitor, bar length = total test count.
Colour: primary competitors `--accent`, secondary `--accent-soft`.
Height: 240px. Label: "A/B test volume by competitor".

---

## Section 4: Test Detail Cards

One card per competitor with at least 1 test. Layout:

```
┌──────────────────────────────────────────────┐
│ Competitor name          [Primary] [N tests] │
│                                              │
│ Timeline:                                    │
│  Feb 07 · screenshots · [pending]            │
│           Screenshot set replaced (5 → 5)   │
│                                              │
│  Mar 14 · title · [pending]                  │
│           "Old title" → "New title"          │
└──────────────────────────────────────────────┘
```

- Timeline entries sorted by date ascending
- Status pills: `pending` (amber), `won` (teal), `lost` (red)
- Screenshots: show only count and date, no URLs
- Title/short_description: show old → new in mono font, full text
- Cards in 2-column grid on desktop, 1-column on mobile

---

## Section 5: Cross-competitor Signals (conditional)

Only render if data contains convergence. If no convergence, omit entirely — no empty state.

Simple table: Field | Competitors | Date range | Signal strength | What it suggests

Signal strength pill: Strong (2 primary), Moderate (1 primary + secondary), Weak (secondary only)

---

## Data Embedding

```javascript
const REPORT_DATA = { /* full JSON */ };
```

All values derived from JS — nothing hardcoded in HTML.

---

## Typography Scale

Same as Track A spec.

| Use               | Font           | Size  | Weight |
|---|---|---|---|
| App name          | Space Grotesk  | 32px  | 700    |
| Section headers   | Space Grotesk  | 22px  | 700    |
| Card headlines    | Space Grotesk  | 18px  | 700    |
| Body / narrative  | Space Grotesk  | 15px  | 400    |
| Old/new values    | JetBrains Mono | 13px  | 400    |
| Pills / badges    | Space Grotesk  | 11px  | 500    |