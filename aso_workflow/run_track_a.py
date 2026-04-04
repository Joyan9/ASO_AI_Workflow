"""
Step 4 — Track A: Extract gaps and fetch keyword metrics

Orchestrates:
1. Transformation (extract terms, build gap list)
2. Metrics fetch (enrich gaps with AppTweak metrics)
3. Final output (write keyword_gaps JSON)
"""

import json
from datetime import datetime
from pathlib import Path

from transformers.track_a import transform_track_a
from fetchers.keywords import fetch_all_gap_metrics

import config


def run_track_a(app_id: str, platform: str, max_gap_metrics: int = 50):
    """
    Run complete Track A pipeline.
    
    Args:
        app_id: Your app ID (iOS bundle ID or Android package name)
        platform: "ios" or "android"
        max_gap_metrics: Max keywords to fetch metrics for (cap for MVP)
    """
    print("=" * 60)
    print(f"Track A — Keyword Gap Analysis ({platform.upper()} {app_id})")
    print("=" * 60)
    print()
    
    # Step 1: Transformation
    print(">>> Step 1: Transformation (extract terms, build gaps)")
    gaps, your_app_summary = transform_track_a(app_id, platform)
    print(f"    Identified {len(gaps)} gap terms")
    print()
    
    # Step 2: Metrics fetch
    print(">>> Step 2: Fetch keyword metrics")
    device = config.iOS_DEVICE if platform.lower() == "ios" else config.ANDROID_DEVICE
    enriched_gaps = fetch_all_gap_metrics(
        gaps,
        platform=platform,
        country=config.COUNTRY,
        language=config.LANGUAGE,
        device=device,
        max_terms=max_gap_metrics,
    )
    print(f"    Enriched {len(enriched_gaps)} gap terms with metrics")
    print()
    
    # Step 3: Build competitor summary
    print(">>> Step 3: Build competitor summary")
    # 1. Path to the main competitors list (e.g., ios_547702041_competitors.json)
    competitors_file = Path(config.DATA_RAW_DIR) / f"{platform}_{app_id}_competitors.json"
    competitor_summary = []

    if competitors_file.exists():
        with open(competitors_file, "r") as f:
            competitors_data = json.load(f)
        
        # 2. Path to the subfolder where individual metadata lives
        comp_metadata_dir = Path(config.DATA_RAW_DIR) / "competitors"
        
        for comp in competitors_data["competitors"]:
            comp_id = comp["app_id"]
            # Look inside the /competitors/ subfolder
            comp_file = comp_metadata_dir / f"{platform}_{comp_id}_metadata.json"
                
            if comp_file.exists():
                with open(comp_file, "r") as f:
                    comp_raw = json.load(f)
                    # Handle both iOS (integer) and Android (string) app IDs
                    comp_meta = comp_raw["result"].get(str(comp_id)) or comp_raw["result"].get(comp_id)
                    if comp_meta:
                        comp_metadata = comp_meta["metadata"]
                        
                        # Count unique terms in this competitor not in your app
                        # For now, we'll use a simple approach: count all gap terms from this competitor
                        unique_count = len([
                            g for g in gaps
                            if comp_id in g["source_apps"]
                        ])
                        
                        competitor_summary.append({
                            "app_id": comp_id,
                            "name": comp_metadata.get("title"),
                            "tier": comp["tier"],
                            "title": comp_metadata.get("title"),
                            "subtitle": comp_metadata.get("subtitle") or comp_metadata.get("short_description"),
                            "unique_terms_not_in_your_app": unique_count,
                        })
    
    print(f"    Built summary for {len(competitor_summary)} competitors")
    print()
    
    # Step 4: Write final output
    print(">>> Step 4: Write final output")
    output_dir = Path(config.DATA_RAW_DIR).parent / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output = {
        "meta": {
            "app_id": app_id,
            "platform": platform,
            "country": config.COUNTRY,
            "run_date": datetime.now().isoformat(),
        },
        "your_app": your_app_summary,
        "keyword_gaps": enriched_gaps,
        "competitor_summary": competitor_summary,
    }
    
    output_file = output_dir / f"keyword_gaps_{platform}_{app_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"    Saved to {output_file}")
    print()
    
    print("=" * 60)
    print("Track A Complete!")
    print("=" * 60)
    
    return output


if __name__ == "__main__":
    # Run for iOS
    run_track_a(config.iOS_APP_ID, "ios")
    
    # Run for Android
    run_track_a(config.ANDROID_APP_ID, "android")
