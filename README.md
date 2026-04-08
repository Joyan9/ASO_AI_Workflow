---
title: ASO Workflow - App Store Optimization Analysis Pipeline
description: A modular pipeline for competitive intelligence in App Store Optimization
author: ASO Team
date: 2026-04-08
version: 1.0
keywords:
  - ASO
  - app-store-optimization
  - competitive-intelligence
  - keyword-analysis
  - a-b-testing
---

# ASO Workflow - App Store Optimization Analysis Pipeline

A modular pipeline for competitive intelligence in App Store Optimization (ASO). Designed to identify optimization opportunities through keyword gap analysis and A/B testing intelligence.

---

## 1. Problem Definition

**Analytical Focus:** Competitor Analysis for App Store Optimization

The App Store Optimization (ASO) landscape is highly competitive. App developers and marketing teams face a critical challenge: *how to identify which terms to target that competitors are ranking for but their own app is not?* Beyond keywords, there's also the question of *what creative and messaging strategies are competitors validating through A/B testing?*

This workflow solves both problems:

- **Track A (Keyword Gap Analysis):** Identifies keyword opportunities where competitors rank but your app does not, prioritized by search volume, difficulty, and competitive presence.
- **Track B (A/B Test Intelligence, Android):** Analyzes competitor A/B testing behavior over the past 90 days to reveal what elements they are actively testing (title, description, screenshots, icons) and whether tests succeeded or are still pending.

The workflow is designed as a reusable intelligence gathering system that can be applied to any mobile app across iOS and Android platforms.

---

## 2. Workflow Design and Structure

![ASO Workflow Diagram](/aso_workflow/ASO_Workflow.png)

The pipeline executes in **6 steps**: 5 automated data-gathering steps followed by 1 AI-powered analysis step:

### Step 1 & 2: Fetch Focus App Metadata & Extract Competitors

**Purpose:** Establish the baseline for your app and identify relevant competitors.

- **Fetch Focus App Metadata** — Pulls current store listing metadata (title, subtitle/description, icon, screenshots) for your target app from AppTweak's metadata endpoint.
  
- **Extract Competitors** — Uses different strategies based on platform:
  - **iOS:** Extracts competitor IDs from the `customers_also_bought` section of your app's metadata. Selects top 3 as primary competitors and next 7 as secondary.
  - **Android:** Calls the Top Charts endpoint for your app's category (e.g., "DATING"). Ranks apps by chart position and selects top 3 as primary, next 7 as secondary.
  
**Output:** Two JSON files per platform with your app metadata and the list of competitors (10 total: 3 primary, 7 secondary).

### Step 3: Fetch Competitor Metadata & History

**Purpose:** Gather the data needed for both analysis tracks.

- Fetches current store listing metadata for each of the 10 competitors (same fields as your app).
- **Android only:** Also fetches the last 90 days of metadata change history, which includes all A/B tests, shipped changes, and their outcomes.

**Output:** 10 metadata JSON files per platform. For Android, also 10 history JSON files (raw change logs).

### Step 4: Track A — Keyword Gap Analysis

**Purpose:** Identify high-value keywords your app is not ranking for.

This track runs a three-step transformation:

1. **Generate Seeds** — Extract all n-grams (1-word, 2-word, 3-word terms) from your app and all competitors' metadata, weighted by field importance (title = 5, subtitle = 4, description excerpt = 3, etc.). Filter to the top 50 most frequent terms not already in your app (gap terms).

2. **Fetch Keyword Rankings** — For each seed keyword, query AppTweak's keyword rankings API to determine:
   - Does your app rank for this keyword? (Yes/No, and at what position if yes)
   - Which competitors rank for it and at what position?
   - Key metrics: search volume, difficulty, number of results, brand status, relevancy scores.

3. **Compute Gaps** — Compare rankings. A "gap term" is one where at least one competitor ranks and your app either doesn't rank or doesn't have ranking data. Sort by:
   - Number of competitors ranking (primary > secondary)
   - Search volume and difficulty metrics
   - Relevancy and intent signals

**Output:** A JSON file with sorted keyword gaps, competitor rankings for each term, and your app's metadata summary.

### Step 5: Track B — A/B Test History (Android Only)

**Purpose:** Understand what store page elements competitors are actively testing.

This track transforms raw metadata change history into structured insights:

1. **Parse History** — Loads the 90-day metadata change log for each Android competitor. Each entry records a change to a field (title, short_description, icon, screenshots) and whether it was an A/B test.

2. **Separate Tests from Shipped Changes** — Distinguishes between:
   - A/B tests (`is_ab_test = true`) — variants that were experimented with, outcome TBD.
   - Shipped changes — final updates that went live and are no longer tests.

3. **Resolve Test Outcomes** — For each pending A/B test, checks if a later shipped change matches one of the test variants:
   - **Won:** A later shipped change matches the test's `new_value` → test was successful and shipped.
   - **Lost:** A later shipped change matches the test's `old_value` → test was abandoned.
   - **Pending:** No matching shipped change found → test is still running or was silently concluded.

4. **Compare Screenshots** — Uses perceptual hashing (pHash) to detect if screenshot sets are identical even if URLs differ (AppTweak rewrites URLs). Caches hashes to avoid redundant downloads.

**Output:** A JSON file with per-competitor test activity, resolved outcomes, and aggregate summaries (total tests, won/lost/pending counts).

### Step 6: AI-Powered Analysis & Report Generation

**Purpose:** Transform raw data output into actionable strategic recommendations using an AI agent.

This step decouples data generation from analysis interpretation. The structured JSON output from either Track A or Track B is passed to an AI agent (like Claude) along with a **reference document** (`analysis_guide.md`) specific to that track.

#### Process Flow:

1. **Prepare Analysis Input** — Take the generated JSON output file:
   - Track A: `keyword_gaps_{platform}_{app_id}.json`
   - Track B: `ab_history_android_{app_id}.json`

2. **Load Reference Guide** — Use the corresponding analysis guide from `reference_documents/`:
   - Track A: `reference_documents/track_a_keyword_gaps/analysis_guide.md`
   - Track B: `reference_documents/track_b_ab_test_inference/analysis_guide.md`

3. **Provide Context to AI Agent** — Present both the JSON output and the analysis guide to the AI agent. The guide serves as:
   - **Analysis Framework** — Instructs the agent on how to interpret the data and identify patterns
   - **Report Structure** — Defines the expected sections (Executive Summary, Key Metrics, Competitor Landscape, etc.)
   - **Metrics Definitions** — Explains technical fields (e.g., KEI, relevancy score, resolved status)
   - **Quality Standards** — Documents what to avoid (e.g., over-interpreting pending A/B tests, including raw screenshot URLs)
   - **Context Awareness** — Provides domain knowledge about ASO practices and industry nuances

4. **Generate Strategic Report** — The AI agent produces:
   - Executive summary with 3–5 prioritized recommendations
   - Detailed analysis tables
   - Cross-competitor insights and trends
   - Actionable next steps for the product team

#### Example Workflow:

```bash
# After running Track A
python run_track_a.py

# In Claude (or another AI agent):
# Prompt: "Analyze this keyword gap data using the attached analysis guide."
# Attachments: 
#   1. keyword_gaps_ios_547702041.json
#   2. reference_documents/track_a_keyword_gaps/analysis_guide.md

# AI Agent Output:
# [Comprehensive report with prioritized gap opportunities, competitive insights, etc.]
```

#### Why This Separation?

- **Modularity** — Data pipeline and analysis interpretation are decoupled. Update analysis logic without re-running costly API calls.
- **Flexibility** — Same output JSON can be analyzed by different AI models or with different prompts.
- **Reusability** — Analysis guides can be refined iteratively and shared across teams.
- **Cost Efficiency** — AI analysis is cheaper than API calls; optimize the expensive part (data fetching) once.

**Output:** A narrative strategic report (markdown, PDF, or dashboard) ready for decision-makers.

---

## 3. Key Logic & Scripts

### Configuration (`config.py`)
Central hub for all pipeline parameters:
- `iOS_APP_ID`, `ANDROID_APP_ID` — Your app identifiers
- `COUNTRY`, `LANGUAGE` — Target market
- `HISTORY_WINDOW_DAYS` — Lookback period (default: 90)
- `TOP_COMPETITORS`, `PRIMARY_TIER_COUNT` — Competitor selection thresholds
- `MAX_SEED_KEYWORDS` — Cap on keywords to fetch ranking data for (default: 50)
- All AppTweak API endpoint URLs
- File paths for raw/processed data

### Fetchers

#### `metadata.py` — Metadata & Competitor Selection
**Key Functions:**
- `AppTweakClient` — Reusable HTTP client that injects the API key header (`X-Apptweak-Key`) and handles error responses.
- `fetch_current_metadata()` — Queries AppTweak's metadata endpoint. Takes app ID, platform, country, device, language. Returns full metadata structure.
- `extract_competitors()` — Intelligently selects 10 competitors based on platform:
  - iOS: Parses `customers_also_bought` list from your app's metadata.
  - Android: Queries the Top Charts endpoint and extracts ranked app IDs.
- `fetch_competitor_metadata()` — Bulk fetches metadata for all 10 competitors, saves to individual files.
- `fetch_competitor_history()` — Android only. Fetches 90-day metadata change history for each competitor.

#### `keywords.py` — Keyword Ranking Metrics
**Key Functions:**
- `fetch_keyword_rankings()` — Expensive operation (10 credits per app/keyword/metric). 
  - Batches requests: max 5 apps per call, max 5 keywords per call.
  - Selects 3 primary + 5 secondary competitors. Fetches rankings for all seed keywords.
  - Saves intermediate results in batch files for resumability and cost auditing.
- `load_existing_ranking_batches()` — Loads previously saved ranking data so you can avoid re-fetching.

### Transformers

#### `track_a.py` — Term Extraction & Gap Computation
**Key Functions:**
- `_extract_app_terms()` — Tokenizes app metadata (title, description, etc.) into unigrams, bigrams, and trigrams. Removes English stopwords and applies field weights.
- `generate_seeds()` — Merges terms from your app and all competitors into a weighted corpus. Filters to gap terms (in competitors but not in your app). Optionally filters via LLM to remove irrelevant keywords (requires Groq API key). Returns top 50.
- `compute_gaps_from_rankings()` — Cross-references ranking data with your app's ranking status. Identifies gaps and sorts by primary competitor count, search volume, and difficulty.

**Weighting System:**
```
title: 5 (highest priority)
subtitle/short_description: 4
promotional_text (iOS): 4
description excerpt (first 250 chars): 3
description remainder: 1 (lowest priority)
```

This ensures terms in high-visibility fields (like title) are surfaced first.

#### `track_b.py` — A/B Test Analysis
**Key Functions:**
- `transform_track_b()` — Main orchestrator for Android history analysis.
- `_screenshot_sets_equal()` — Compares screenshot sets using perceptual hashing (pHash) to detect identity despite URL changes. Falls back to URL comparison if image libraries unavailable.
- `_resolve_ab_test()` — For each A/B test, checks if a later shipped change matches either the test's old or new value. Returns resolution status (won/lost/pending).
- Per-competitor summaries with test counts, field distribution, and timeline.

### Entry Points

#### `run_fetcher.py`
Orchestrates Steps 1-3: Fetches your app metadata, extracts competitors, then fetches all competitor data.

#### `run_track_a.py` (Step 4)
Orchestrates keyword gap analysis: generates seeds, fetches rankings, computes gaps, outputs final JSON.

#### `run_track_b.py` (Step 5)
Orchestrates A/B test analysis for Android: transforms history, resolves tests, outputs final JSON.

---

## 4. Data Sources & API Endpoints

### AppTweak API

All endpoints use the AppTweak public API (v1). Authentication via `X-Apptweak-Key` header.

| Endpoint | Purpose | Implementation | Credits Cost |
|----------|---------|-----------------|--------------|
| `api/public/store/apps/metadata.json` | Fetch current app metadata | `fetch_current_metadata()` | 1 per call |
| `api/public/store/charts/top-results/current.json` | Fetch category top charts (Android) | `extract_competitors()` | 1 per call |
| `api/public/store/apps/metadata/changes.json` | Fetch 90-day metadata change history | `fetch_competitor_history()` | 1 per call |
| `api/public/store/apps/keywords-rankings/current.json` | Fetch keyword rankings (platform, app, keywords, metrics) | `fetch_keyword_rankings()` | 10 per app/keyword/metric combo |


### Optional: Groq API (LLM Filtering)

For Track A's seed generation, the pipeline can optionally filter extracted keywords through a Groq-based LLM to remove irrelevant terms (e.g., developer names, brand terms). This step:
- Requires `GROQ_API_KEY` in `.env`
- Calls `groq.Completion.create()` with a curated prompt
- Is optional (skip if you want all raw terms)

---

## 5. Reusability: Adapting to Other Apps & Analysis Types

### For Other Mobile Apps

The pipeline is **fully parameterized** for easy reuse:

1. **Update `config.py`:**
   - Change `iOS_APP_ID` and `ANDROID_APP_ID` to your target app
   - Adjust `COUNTRY` and `LANGUAGE` if analyzing a different market
   - Optionally adjust `PRIMARY_TIER_COUNT` or `HISTORY_WINDOW_DAYS`

2. **Run the pipeline:**
   ```bash
   python run_fetcher.py          # Steps 1-3
   python run_track_a.py          # Step 4 (both platforms)
   python run_track_b.py          # Step 5 (Android only)
   ```

3. **Output files** are saved under `data/processed/` with the new app ID in the filename, so multiple apps can coexist.

### For Other Analysis Types

The modular architecture supports extending to new analysis tracks:

#### Example: Track C — Historical Ranking Trends
- Reuse the metadata history fetcher (`fetch_competitor_history()`).
- Add a new transformer module (`transformers/track_c.py`) to extract ranking trajectory (e.g., "Competitors' ranking positions rose by X in the past 30 days").
- Create a new entry point (`run_track_c.py`).

#### Example: Track D — Screenshot & Icon Trends
- Reuse `track_b.py`'s screenshot comparison logic (`_screenshot_sets_equal()`).
- Build a new view focusing on visual creative patterns (color, layout, UI elements).
- Use perceptual hashing to detect visual similarities across competitors.

**Key Takeaway:** The pipeline is built on three reusable pillars — (1) metadata fetching, (2) competitor selection, (3) transformation logic — allowing rapid prototyping of new analysis tracks without rebuilding the foundation.

---

## 6. Assumptions

The pipeline makes the following assumptions about your setup and the data:

1. **Primary vs. Secondary Weighting** — The pipeline assumes primary competitors (top 3) are more important than secondary (next 7). In some niches, secondary competitors may be equally relevant. Adjust thresholds in `config.py` if needed.
2. **Field Weighting Relevance** — The field weights (title: 5, description: 1) are based on ASO best practices but may not apply to all categories. Gaming apps, for example, may emphasize different fields than dating apps.
3. **90-Day History Window** — This is arbitrary and chosen for API cost efficiency. Longer windows provide more signal but cost more credits. Adjust `HISTORY_WINDOW_DAYS` for your analysis.
4. **A/B Test Resolution Accuracy** — Track B resolves A/B tests by checking if later shipped changes match test variants. However, if a competitor runs a test, ships partial changes, or manually tweaks besides tests, resolution may be inaccurate.

5. **Market Maturity** — The pipeline assumes the selected market (country/language) has sufficient app ecosystem data in AppTweak (i.e., at least 10 similar apps exist).

---

## 7. Limitations

The pipeline has the following known limitations:

### Functional Limitations

1. **Competitors Limited to Top 10** — The pipeline selects only 3 primary + 7 secondary competitors (configurable but not scalable to 100+). This is a cost optimization to avoid excessive API credits. For niche apps with few competitors, you may see gaps that should include secondary competitors.

2. **LLM Filtering is Experimental** — The optional Track A LLM filter (Groq-based) removes "irrelevant" keywords, but LLM quality varies. False positives (filtering good keywords) are possible. This step is optional; run without it if uncertain.

3. **Unigram/Bigram/Trigram Extraction** — The transformer only extracts up to 3-word phrases. Longer, niche keywords (4+ words) are not captured, which may miss very specific long-tail terms.

4. **No Smart Caching Across Runs** — While the pipeline saves ranking batches locally, it does not deduplicate if you re-run with overlapping keyword lists. Rerunning Track A with the same app may incur duplicate API charges.


5. **Stopwords are English-Only** — The NLP tokenizer removes English stopwords. For non-English apps or markets, stopword filtering may be ineffective, leading to false positives (e.g., French "le" or "la" may remain).

6. **No Sentiment or Intent Analysis** — The pipeline identifies gaps by presence alone. It does not estimate intent (is this keyword for users seeking dating, safety, profiles?), so you must manually perform intent bucketing.

---

## Getting Started

### 1. Install Dependencies

```bash
cd aso_workflow
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the `aso_workflow/` directory:

```
APPTWEAK_API_KEY=your_apptweak_api_key_here
GROQ_API_KEY=your_groq_key_here  # Optional, only needed if using LLM filtering
```

Do not commit `.env` to version control.

### 3. Update Configuration (If Needed)

Edit `config.py` to change your target apps, market, or history window:

```python
iOS_APP_ID = "your_ios_app_id"          # E.g., "547702041"
ANDROID_APP_ID = "your_android_app_id"  # E.g., "com.example.app"
COUNTRY = "us"                           # Target country code
LANGUAGE = "us"                          # Target language code
HISTORY_WINDOW_DAYS = 90                 # Android history lookback
```

### 4. Run the Pipeline

```bash
# Steps 1-3: Fetch your app and competitor metadata
python run_fetcher.py

# Step 4: Run Track A (Keyword Gap Analysis)
python run_track_a.py

# Step 5: Run Track B (A/B Test History — Android only)
python run_track_b.py
```

Output files are saved to `data/processed/`:
- `keyword_gaps_{platform}_{app_id}.json` — Track A results
- `ab_history_android_{app_id}.json` — Track B results

---

## Using the Analysis Guides

The analysis guides serve as detailed prompts for your AI agent:

- [Track A — Keyword Gap Analysis Guide](reference_documents/track_a_keyword_gaps/analysis_guide.md) — Frameworks for prioritizing keyword opportunities and understanding competitive landscape

- [Track B — A/B Test Intelligence Guide](reference_documents/track_b_ab_test_inference/analysis_guide.md) — Guidelines for interpreting competitor testing behavior and extracting strategy signals

---

## 8. Project Structure

```
ASO_AI_Workflow/
├── README.md                                 # This file
├── requirements.txt                          # Python dependencies
├── aso_workflow/
│   ├── __init__.py                          # Package initialization
│   ├── config.py                            # Central configuration
│   ├── run_fetcher.py                       # Entry point: Steps 1-3
│   ├── run_track_a.py                       # Entry point: Step 4
│   ├── run_track_b.py                       # Entry point: Step 5
│   ├── fetchers/                            # Data fetch modules
│   │   ├── __init__.py
│   │   ├── metadata.py                      # Metadata & competitor extraction
│   │   └── keywords.py                      # Keyword ranking fetcher
│   ├── transformers/                        # Data transformation modules
│   │   ├── __init__.py
│   │   ├── track_a.py                       # Keyword gap analysis
│   │   └── track_b.py                       # A/B test history analysis
│   └── data/
│       ├── raw/                             # Raw API responses
│       │   ├── competitors/                 # Competitor metadata & history
│       │   ├── keyword_rankings/            # Ranking batch files
│       │   └── screenshot_hashes/           # Cached perceptual hashes
│       └── processed/                       # Final analysis output JSON files
├── reference_documents/                     # AI agent prompts & guides
│   ├── track_a_keyword_gaps/
│   │   └── analysis_guide.md                # Track A analysis framework
│   └── track_b_ab_test_inference/
│       └── analysis_guide.md                # Track B analysis framework
├── AppTweak_Documentation_Links.md          # API endpoint reference
└── .env                                     # API keys (not in repo)
```

---

## 9. Troubleshooting

### Common Issues

**Issue:** `APPTWEAK_API_KEY not found in .env file`
- **Solution:** Create `.env` in the `aso_workflow/` directory with `APPTWEAK_API_KEY=your_key`

**Issue:** `No data found for keyword rankings`
- **Solution:** Ensure Track A seed generation succeeded. Check logs for blocked keywords or API errors.

**Issue:** Screenshots not comparing correctly in Track B
- **Solution:** Ensure PIL and imagehash libraries are installed: `pip install Pillow imagehash`. The pipeline falls back to URL comparison if image libraries are unavailable.

**Issue:** Groq filtering removes too many keywords
- **Solution:** The LLM filter is optional. Run Track A without it by editing `config.py` (set `GROQ_API_KEY` to empty).

---

## 10. Contributing & Future Extensions

### Adding New Analysis Tracks

The modular architecture makes it easy to add new analysis capabilities:

1. Create a new transformer in `aso_workflow/transformers/` (e.g., `track_c.py`)
2. Create an entry point script `run_track_c.py`
3. Add a reference document in `reference_documents/track_c/analysis_guide.md`
4. Reuse existing fetchers for data gathering

### Improving Competitor Selection

To refine how competitors are selected:
- Edit `extract_competitors()` in `aso_workflow/fetchers/metadata.py`
- Modify `PRIMARY_TIER_COUNT` and `TOP_COMPETITORS` in `config.py`

### Extending Transformation Logic

To add new metrics or analysis:
- Edit transformation functions in `aso_workflow/transformers/track_*.py`
- Enhance the output JSON schema as needed
- Update the corresponding `analysis_guide.md` reference document

---

## 11. Credits & Resources

- **AppTweak API Documentation:** https://developers.apptweak.com/
- **ASO Best Practices:** Consult industry guides on App Store Optimization
- **AI Agent Prompting:** Reference documents designed for use with Claude or similar LLMs

---

## License

This project is provided as-is for ASO and competitive intelligence analysis. Ensure you have appropriate API access and comply with all data usage agreements.



