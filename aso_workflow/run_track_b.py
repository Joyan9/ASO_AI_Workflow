"""
Step 5 — Track B: Android A/B test history analysis

Orchestrates:
1. Load competitor history files
2. Filter to relevant fields (title, short_description, icon, screenshots)
3. Separate A/B tests from shipped changes
4. Resolve A/B tests (won/lost/pending)
5. Output final JSON with competitor A/B history and summaries
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
