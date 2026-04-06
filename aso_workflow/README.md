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

The pipeline executes in **5 sequential steps** with optional branching for platform-specific analysis:

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

After running the pipeline, use the analysis guides as prompts to an LLM like Claude which will create a report:

- [Track A — Keyword Gap Analysis Guide](reference_documents/track_a_keyword_gaps/analysis_guide.md)
- [Track B — A/B Test Intelligence Guide](reference_documents/track_b_ab_test_inference/analysis_guide.md)

---

## Troubleshooting

**API Key Issues:** Ensure your `.env` file is in `aso_workflow/` and properly formatted. Verify the key is active on AppTweak.

**No Competitors Found:** The app may not exist in the target market or category. Check that the app ID and platform are correct.

**Ranking Data is Sparse:** Some keywords may not have ranking data in the target market. This is normal. The output will show `null` for unavailable metrics.

**Screenshot Comparison Fails:** Install image libraries with `pip install Pillow imagehash`. Without these, the pipeline falls back to URL-based comparison.



