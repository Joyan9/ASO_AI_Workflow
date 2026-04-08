"""
Keyword Metrics Fetcher — Fetch metrics for gap terms from AppTweak

This module fetches current keyword metrics (volume, difficulty, results, brand)
for each gap term identified by the transformation step.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import quote

from .metadata import AppTweakClient

import config


def fetch_keyword_rankings(
    platform: str,
    your_app_id: str,
    seed_keywords: List[str],
) -> Dict[str, Any]:
    """Fetch keyword rankings from AppTweak for your app and competitors.
    
    Queries the Keyword Rankings endpoint for seed keywords, fetching ranking data
    for your app and selected competitors (3 primary + 5 secondary). Results are
    batched for API efficiency and saved to local batch files for resumability.
    
    This is an expensive operation (10 credits per app/keyword/metric combo):
        - Max 5 apps per call
        - Max 5 keywords per call
        - Total calls = ceil(n_apps / 5) × ceil(n_keywords / 5)
    
    Args:
        platform: "ios" or "android"
        your_app_id: Your app's ID
        seed_keywords: List of keywords to fetch rankings for (max config.MAX_SEED_KEYWORDS)
    
    Returns:
        Merged ranking data structure with keys:
            - meta: Metadata (platform, run_date, seeds_with_data, etc.)
            - keywords: List of keyword dicts each containing:
                - term: Keyword string
                - your_app: Dict with ranking info (rank, installs, relevancy, kei, chance)
                - competitors: List of competitor ranking dicts
    
    Saves:
        data/raw/keyword_rankings/{platform}_{app_id}_batch_*.json for each request batch
    
    Note:
        This is a costly operation. Budget credits accordingly.
        Existing batches saved locally will be reused if re-running.
    """
    from .metadata import API_KEY, AppTweakClient
    
    print("\n[RANKINGS] ========================================")
    print("[RANKINGS] Fetch keyword rankings")
    print("[RANKINGS] ========================================\n")
    
    client = AppTweakClient(API_KEY)
    
    # Get config values
    country = config.COUNTRY
    language = config.LANGUAGE
    device = config.iOS_DEVICE if platform.lower() == "ios" else config.ANDROID_DEVICE
    
    # Load competitor list with tier info
    raw_dir = Path(config.DATA_RAW_DIR)
    competitors_file = raw_dir / f"{platform}_{your_app_id}_competitors.json"
    
    with open(competitors_file, "r") as f:
        competitors_data = json.load(f)
    
    all_competitors = competitors_data["competitors"]
    
    # Select competitor apps to fetch
    if platform.lower() == "ios":
        primary_competitors = [c["app_id"] for c in all_competitors if c["tier"] == "primary"][:3]
        secondary_competitors = [c["app_id"] for c in all_competitors if c["tier"] == "secondary"][:5]
    else:  # android
        primary_competitors = [c["app_id"] for c in all_competitors if c["tier"] == "primary"][:3]
        secondary_competitors = [c["app_id"] for c in all_competitors if c["tier"] == "secondary"][:5]
    
    apps_to_fetch = [your_app_id] + primary_competitors + secondary_competitors
    app_tiers = {your_app_id: "your_app"}
    for comp in all_competitors:
        if comp["app_id"] in apps_to_fetch:
            app_tiers[comp["app_id"]] = comp["tier"]
    
    keywords_to_fetch = seed_keywords
    
    # Calculate cost estimate
    n_app_batches = (len(apps_to_fetch) + 4) // 5  # ceil division
    n_keyword_batches = (len(keywords_to_fetch) + 4) // 5
    n_total_calls = n_app_batches * n_keyword_batches
    n_metrics = len(config.KEYWORD_RANKINGS_METRICS.split(","))
    estimated_credits = len(apps_to_fetch) * len(keywords_to_fetch) * n_metrics * config.CREDIT_PER_APP_KEYWORD_METRIC
    
    print(f"[RANKINGS] Apps to fetch: {len(apps_to_fetch)} (your app + {len(primary_competitors)} primary + {len(secondary_competitors)} secondary)")
    print(f"[RANKINGS] Keywords to fetch: {len(keywords_to_fetch)}")
    print(f"[RANKINGS] Batching: {n_app_batches} app batches × {n_keyword_batches} keyword batches = {n_total_calls} calls")
    print(f"[RANKINGS] Metrics per call: {n_metrics} ({config.KEYWORD_RANKINGS_METRICS})")
    print(f"[RANKINGS] Estimated credit cost: {estimated_credits} credits ({len(apps_to_fetch)} apps × {len(keywords_to_fetch)} keywords × {n_metrics} metrics × 10 credits)")
    print()
    
    if config.KEYWORD_RANKINGS_DRY_RUN:
        print("[RANKINGS] ⚠️  DRY-RUN MODE ENABLED (no API calls will be made)")
        print("[RANKINGS] Set KEYWORD_RANKINGS_DRY_RUN=False in config.py to execute")
        print()
        return {
            "meta": {
                "platform": platform,
                "your_app_id": your_app_id,
                "apps_count": len(apps_to_fetch),
                "keywords_count": len(keywords_to_fetch),
                "estimated_credits": estimated_credits,
                "dry_run": True,
            },
            "keywords": [],
        }
    
    print("[RANKINGS] Fetching keyword rankings (please review cost above)...")
    print()
    
    # Batch apps and keywords
    app_batches = [apps_to_fetch[i:i+5] for i in range(0, len(apps_to_fetch), 5)]
    keyword_batches = [keywords_to_fetch[i:i+5] for i in range(0, len(keywords_to_fetch), 5)]
    
    # Save directory
    rankings_dir = raw_dir / "keyword_rankings"
    rankings_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch batches
    all_responses = {}
    batch_counter = 0
    
    for app_batch_idx, app_batch in enumerate(app_batches):
        for kw_batch_idx, kw_batch in enumerate(keyword_batches):
            batch_counter += 1
            batch_id = f"{platform}_{your_app_id}_batch_{batch_counter}"
            
            print(f"[RANKINGS] Batch {batch_counter}/{n_total_calls}: apps {app_batch_idx*5+1}-{min((app_batch_idx+1)*5, len(apps_to_fetch))}, keywords {kw_batch_idx*5+1}-{min((kw_batch_idx+1)*5, len(keywords_to_fetch))}")
            
            # Make API call
            apps_param = ",".join(str(a) for a in app_batch)
            keywords_param = ",".join(kw_batch)
            
            params = {
                "apps": apps_param,
                "keywords": keywords_param,
                "metrics": config.KEYWORD_RANKINGS_METRICS,
                "country": country,
                "language": language,
                "device": device,
            }
            
            try:
                response = client.get(config.KEYWORD_RANKINGS_ENDPOINT, params=params)
                
                # Save raw response
                batch_file = rankings_dir / f"{batch_id}.json"
                with open(batch_file, "w") as f:
                    json.dump(response, f, indent=2)
                
                # Merge into all_responses
                all_responses[batch_id] = response
                print(f"[RANKINGS]   ✓ Saved to {batch_file}")
                
            except Exception as e:
                print(f"[RANKINGS]   ✗ Error: {e}")
                all_responses[batch_id] = {"error": str(e), "result": {}}
            
            # Sleep between calls
            if batch_counter < n_total_calls:
                time.sleep(0.5)
    
    print()
    print(f"[RANKINGS] Completed {batch_counter} API calls")
    print()
    
    # Now merge the responses into a unified keyword-centric structure
    merged_rankings = _merge_ranking_responses(your_app_id, all_responses, app_tiers, platform)
    
    return merged_rankings


def _merge_ranking_responses(
    your_app_id: str,
    batch_responses: Dict[str, Any],
    app_tiers: Dict[str, str],
    platform: str,
) -> Dict[str, Any]:
    """
    Merge batched ranking responses into a unified per-keyword structure.
    
    API metric structure: each metric is {"value": X, "fetch_performed": bool, "effective_value": Y}
    
    Returns:
        {
            "meta": { ... },
            "keywords": [
                {
                    "term": "keyword",
                    "your_app": { "ranked": bool, "rank": int or null, ... },
                    "competitors": [ { ... } ]
                }
            ]
        }
    """
    print("[RANKINGS] Merging responses...")
    
    # Collect all keywords and their data
    keyword_data = {}  # keyword -> {your_app, competitors}
    
    for batch_id, response in batch_responses.items():
        if "error" in response:
            continue
        
        result = response.get("result", {})
        
        for app, app_results in result.items():
            for keyword, metrics in app_results.items():
                if keyword not in keyword_data:
                    keyword_data[keyword] = {
                        "your_app": None,
                        "competitors": [],
                    }
                
                # Extract rank and fetch_performed from the nested structure
                rank_data = metrics.get("rank", {})
                if isinstance(rank_data, dict):
                    rank_value = rank_data.get("value")
                    fetch_performed = rank_data.get("fetch_performed", False)
                else:
                    rank_value = rank_data
                    fetch_performed = metrics.get("fetch_performed", False)
                
                # Determine if app is ranked: value is not null and fetch was performed
                ranked = rank_value is not None and fetch_performed
                
                # Extract other metrics, handling both nested and scalar formats
                def extract_metric(metric_name):
                    metric_val = metrics.get(metric_name)
                    if isinstance(metric_val, dict):
                        return metric_val.get("value")
                    return metric_val
                
                ranking_entry = {
                    "app_id": app,
                    "tier": app_tiers.get(app, "unknown"),
                    "ranked": ranked,
                    "rank": rank_value,
                    "fetch_performed": fetch_performed,
                    "installs": extract_metric("installs"),
                    "relevancy": extract_metric("relevancy"),
                    "kei": extract_metric("kei"),
                    "chance": extract_metric("chance"),
                }
                
                if app == your_app_id:
                    keyword_data[keyword]["your_app"] = ranking_entry
                else:
                    keyword_data[keyword]["competitors"].append(ranking_entry)
    
    # Build final output
    keywords_output = []
    for keyword, data in sorted(keyword_data.items()):
        keywords_output.append({
            "term": keyword,
            "your_app": data["your_app"] or {
                "ranked": False,
                "rank": None,
                "fetch_performed": False,
            },
            "competitors": data["competitors"],
        })
    
    print(f"[RANKINGS] Merged data for {len(keywords_output)} keywords")
    print()
    
    return {
        "meta": {
            "platform": platform,
            "your_app_id": your_app_id,
            "keywords_count": len(keywords_output),
            "merged_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "keywords": keywords_output,
    }


def load_existing_ranking_batches(
    platform: str,
    your_app_id: str,
) -> Dict[str, Any]:
    """
    Load and merge existing ranking batch files from data/raw/keyword_rankings/.
    
    This is useful when ranking data has already been fetched and saved.
    Looks for files matching pattern: {platform}_{app_id}_batch_*.json
    
    Args:
        platform: "ios" or "android"
        your_app_id: Your app ID
    
    Returns:
        Merged ranking data structure (same as fetch_keyword_rankings)
        Returns empty keywords if no batch files found
    """
    print("\n[RANKINGS] ========================================")
    print("[RANKINGS] Load existing ranking batch files")
    print("[RANKINGS] ========================================\n")
    
    raw_dir = Path(config.DATA_RAW_DIR)
    rankings_dir = raw_dir / "keyword_rankings"
    
    # Check if rankings directory exists
    if not rankings_dir.exists():
        print("[RANKINGS] No ranking batches directory found")
        return {
            "meta": {
                "platform": platform,
                "your_app_id": your_app_id,
                "keywords_count": 0,
                "source": "none",
            },
            "keywords": [],
        }
    
    # Find all batch files for this platform/app
    batch_pattern = f"{platform}_{your_app_id}_batch_*.json"
    batch_files = sorted(rankings_dir.glob(batch_pattern))
    
    if not batch_files:
        print(f"[RANKINGS] No batch files found matching: {batch_pattern}")
        return {
            "meta": {
                "platform": platform,
                "your_app_id": your_app_id,
                "keywords_count": 0,
                "source": "none",
            },
            "keywords": [],
        }
    
    print(f"[RANKINGS] Found {len(batch_files)} batch files")
    
    # Load all batch files
    batch_responses = {}
    for batch_file in batch_files:
        batch_id = batch_file.stem  # e.g., "ios_547702041_batch_1"
        try:
            with open(batch_file, "r") as f:
                response = json.load(f)
            batch_responses[batch_id] = response
            print(f"[RANKINGS]   ✓ Loaded {batch_id}")
        except Exception as e:
            print(f"[RANKINGS]   ✗ Error loading {batch_id}: {e}")
    
    if not batch_responses:
        print("[RANKINGS] Failed to load any batch files")
        return {
            "meta": {
                "platform": platform,
                "your_app_id": your_app_id,
                "keywords_count": 0,
                "source": "none",
            },
            "keywords": [],
        }
    
    print()
    
    # Load competitor information to get tier mapping
    competitors_file = raw_dir / f"{platform}_{your_app_id}_competitors.json"
    app_tiers = {your_app_id: "your_app"}
    
    if competitors_file.exists():
        with open(competitors_file, "r") as f:
            competitors_data = json.load(f)
        for comp in competitors_data.get("competitors", []):
            app_tiers[comp["app_id"]] = comp["tier"]
    
    # Merge the loaded batches
    merged = _merge_ranking_responses(your_app_id, batch_responses, app_tiers, platform)
    
    # Add metadata about source
    merged["meta"]["source"] = "loaded_from_batches"
    merged["meta"]["batch_count"] = len(batch_responses)
    
    return merged
