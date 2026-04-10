"""
Step 4 — Track A: Keyword Gap Analysis via AppTweak Rankings

Identifies high-value keywords where competitors rank but your app does not.
Executes a 4-step pipeline:

    1. Generate seeds — Extract n-grams (1-word, 2-word, 3-word) from your app and competitors'
       metadata, weighted by field importance. Filter to top 50 gap terms (in competitors but not in your app).

    2. Load/Fetch rankings — Either load previously saved ranking batches or fetch fresh data
       from AppTweak. Batches requests for API efficiency (max 5 apps × 5 keywords per call).

    3. Compute gaps — Cross-reference ranking data. A gap is a term where at least one competitor
       ranks and your app either doesn't rank or has no ranking data. Sort by competitor presence,
       search volume, and difficulty.

    4. Write output — Save structured JSON with keyword gaps, competitor rankings per term,
       and competitive landscape summary.

Output file: data/processed/keyword_gaps_{platform}_{app_id}.json

Run from the aso_workflow directory:
    python run_track_a.py
"""

import json
from datetime import datetime
from pathlib import Path

from transformers.track_a import (
    generate_seeds,
    compute_gaps_from_rankings,
    filter_gaps_by_volume_metrics,
)
from fetchers.keywords import fetch_keyword_rankings, load_existing_ranking_batches

import config


def run_track_a(app_id: str, platform: str):
    """
    Run complete Track A pipeline using keyword rankings.
    
    Args:
        app_id: Your app ID (iOS bundle ID or Android package name)
        platform: "ios" or "android"
    """
    print("\n")
    print("=" * 70)
    print(f"TRACK A — KEYWORD GAP ANALYSIS ({platform.upper()} {app_id})")
    print("=" * 70)
    
    # Step 1: Generate seeds
    print()
    seeds = generate_seeds(app_id, platform)
    
    if not seeds:
        print("[ERROR] No seeds generated. Aborting.")
        return None
    
    # Step 2: Load/Fetch rankings
    print()
    
    raw_dir = Path(config.DATA_RAW_DIR)
    rankings_dir = raw_dir / "keyword_rankings"
    batch_pattern = f"{platform}_{app_id}_batch_*.json"
    existing_batches = list(rankings_dir.glob(batch_pattern)) if rankings_dir.exists() else []
    
    # If dry-run is disabled, always fetch fresh data (ignore existing batches)
    if not config.KEYWORD_RANKINGS_DRY_RUN:
        print("[RUN] Fetching fresh ranking data (dry-run mode disabled)...")
        ranking_data = fetch_keyword_rankings(platform, app_id, seeds)
    # In dry-run mode, try to load existing batches
    elif existing_batches:
        print(f"[RUN] Found {len(existing_batches)} existing ranking batch files. Loading them...")
        ranking_data = load_existing_ranking_batches(platform, app_id)
    else:
        print("[RUN] No existing ranking batches found. Fetching them...")
        ranking_data = fetch_keyword_rankings(platform, app_id, seeds)
        
        print("[RUN] Dry-run mode is enabled. Skipping gap computation.")
        print("[RUN] To execute live and fetch ranking data, set KEYWORD_RANKINGS_DRY_RUN = False in config.py")
        print()
        return ranking_data
    
    # Step 3: Compute gaps from ranking data
    print()
    gaps, your_app_summary = compute_gaps_from_rankings(app_id, platform, ranking_data)
    
    if not gaps:
        print("[GAPS] No gaps found. Check that competitors are ranked for keywords.")
        print()
        gaps_before_volume_filter = 0
        filter_summary = {}
    else:
        gaps_before_volume_filter = len(gaps)
        
        # Step 4: Filter gaps by volume threshold using AppTweak metrics
        print()
        gaps, filter_summary = filter_gaps_by_volume_metrics(
            gaps=gaps,
            platform=platform,
            volume_threshold=config.MIN_VOLUME_THRESHOLD,
            country=config.COUNTRY,
            language=config.LANGUAGE,
        )
    
    # Step 5: Build competitor summary
    print("\n[OUTPUT] Building competitor summary...")
    
    competitors_file = Path(config.DATA_RAW_DIR) / f"{platform}_{app_id}_competitors.json"
    competitor_summary = []
    
    if competitors_file.exists():
        with open(competitors_file, "r") as f:
            competitors_data = json.load(f)
        
        for comp in competitors_data["competitors"]:
            comp_id = comp["app_id"]
            comp_metadata_dir = Path(config.DATA_RAW_DIR) / "competitors"
            comp_file = comp_metadata_dir / f"{platform}_{comp_id}_metadata.json"
            
            if comp_file.exists():
                with open(comp_file, "r") as f:
                    comp_raw = json.load(f)
                    comp_meta = comp_raw["result"].get(str(comp_id)) or comp_raw["result"].get(comp_id)
                    if comp_meta:
                        comp_metadata = comp_meta["metadata"]
                        
                        # Count gaps where this competitor is ranked
                        gaps_count = len([g for g in gaps if comp_id in g["source_apps"]])
                        
                        competitor_summary.append({
                            "app_id": comp_id,
                            "name": comp_metadata.get("title"),
                            "tier": comp["tier"],
                            "gaps_ranked_for": gaps_count,
                        })
    
    print(f"[OUTPUT] Built summary for {len(competitor_summary)} competitors")
    
    # Step 6: Write final output
    print("[OUTPUT] Writing keyword_gaps JSON...")
    
    output_dir = Path(config.DATA_RAW_DIR).parent / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Count seeds with ranking data
    seeds_with_data = len([k for k in ranking_data.get("keywords", []) if k["your_app"]])
    
    output = {
        "meta": {
            "app_id": app_id,
            "platform": platform,
            "country": config.COUNTRY,
            "run_date": datetime.now().isoformat(),
            "seeds_generated": len(seeds),
            "seeds_with_ranking_data": seeds_with_data,
            "gaps_before_volume_filter": gaps_before_volume_filter,
            "gaps_after_volume_filter": len(gaps),
            "volume_threshold": config.MIN_VOLUME_THRESHOLD,
            "volume_filter_summary": filter_summary,
        },
        "your_app": your_app_summary,
        "keyword_gaps": gaps,
        "competitor_summary": competitor_summary,
    }
    
    output_file = output_dir / f"keyword_gaps_{platform}_{app_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"[OUTPUT] Saved to {output_file}")
    print()
    
    print("=" * 70)
    print("TRACK A COMPLETE")
    print("=" * 70)
    print(f"  Seeds generated:        {len(seeds)}")
    print(f"  Seeds with data:        {seeds_with_data}")
    print(f"  Gaps identified:        {len(gaps)}")
    print(f"  Competitors analyzed:   {len(competitor_summary)}")
    print("=" * 70)
    print()
    
    return output


if __name__ == "__main__":
    # Run for iOS
    print("\n" + "=" * 70)
    print("TRACK A — iOS")
    print("=" * 70)
    run_track_a(config.iOS_APP_ID, "ios")
    
    # Run for Android
    print("\n" + "=" * 70)
    print("TRACK A — Android")
    print("=" * 70)
    run_track_a(config.ANDROID_APP_ID, "android")
