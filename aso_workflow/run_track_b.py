"""
Step 5 — Track B: Android A/B Test History Analysis

Analyzes competitor A/B testing behavior over the past 90 days to reveal what elements
they are validating (title, description, screenshots, icons) and test outcomes.

Executes a 5-step transformation pipeline:

    1. Load history — Fetches raw 90-day metadata change history for each Android competitor.
       Each entry records a change to a field with metadata (type, date, A/B test flag).

    2. Filter changes — Extracts only relevant fields: title, short_description, icon, screenshots.
       Ignores other metadata fields like rating summary or release notes.

    3. Separate tests from shipped — Distinguishes between:
       - A/B tests (is_ab_test=true): Variants experimenting with creative/copy
       - Shipped changes: Final updates that went live without testing

    4. Resolve test outcomes — For each pending A/B test, checks if a later shipped change
       matches the test's new_value (Won), old_value (Lost), or neither (Pending).
       Uses perceptual hashing (pHash) for screenshot comparison to account for AppTweak URL rewrites.

    5. Generate summaries — Per-competitor test activity including counts, field distribution,
       and timeline. Also produces aggregate metrics and text variant deduplication.

Output file: data/processed/ab_history_android_{app_id}.json

Requirements:
    - Competitor history files must exist from run_fetcher.py
    - Optional: PIL and imagehash for screenshot comparison (falls back to URL comparison)

Run from the aso_workflow directory:
    python run_track_b.py
"""

import json
from datetime import datetime
from pathlib import Path

from transformers.track_b import transform_track_b

import config


def run_track_b(app_id: str):
    """
    Run complete Track B pipeline for Android A/B test history.
    
    Args:
        app_id: Android app ID (package name, e.g., "com.tinder")
    """
    print("=" * 60)
    print(f"Track B — Android A/B Test History Analysis ({app_id})")
    print("=" * 60)
    print()
    
    # Run transformation
    target_app, competitors, summary = transform_track_b(app_id)
    
    # Write output
    print(">>> Writing output JSON...")
    output_dir = Path(config.DATA_RAW_DIR).parent / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract text variants from summary
    text_variants = summary.pop("text_variants", {})
    
    output = {
        "meta": {
            "platform": "android",
            "country": config.COUNTRY,
            "run_date": datetime.now().isoformat(),
            "history_window_days": config.HISTORY_WINDOW_DAYS,
        },
        "target_app": target_app,
        "summary": summary,
        "competitors": competitors,
    }
    
    # Add text variants at root if non-empty
    if text_variants:
        output["text_variants"] = text_variants
    
    output_file = output_dir / f"ab_history_android_{app_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"    Saved to {output_file}")
    print()
    
    print("=" * 60)
    print("Track B Complete!")
    print("=" * 60)
    
    return output


if __name__ == "__main__":
    run_track_b(config.ANDROID_APP_ID)
