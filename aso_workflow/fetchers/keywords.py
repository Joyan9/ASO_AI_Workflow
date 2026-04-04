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


def fetch_keyword_metrics(
    keywords: List[str],
    platform: str = "ios",
    country: str = "us",
    language: str = "us",
    device: str = "iphone",
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch metrics for a batch of keywords (max 5 per call per API docs).
    
    Returns dict of {keyword: {volume, difficulty, results, brand, max_reach}}
    """
    from .metadata import API_KEY
    
    client = AppTweakClient(API_KEY)
    
    if len(keywords) > 5:
        raise ValueError("AppTweak API supports max 5 keywords per call")
    
    # Comma-separated keywords, URL-encoded
    keywords_param = ",".join(keywords)
    metrics_param = "volume,difficulty,results,brand,all_installs"
    
    params = {
        "keywords": keywords_param,
        "metrics": metrics_param,
        "country": country,
        "language": language,
        "device": device,
    }
    
    endpoint = "api/public/store/keywords/metrics/current.json"
    
    print(f"[METRICS] Fetching {len(keywords)} keywords...")
    response = client.get(endpoint, params=params)
    
    # Parse response into keyword -> metrics map
    metrics_map = {}
    
    result = response.get("result", {})
    for keyword, metrics_data in result.items():
        # Extract values from the nested structure
        metrics_map[keyword] = {
            "volume": metrics_data.get("volume", {}).get("value") if isinstance(metrics_data.get("volume"), dict) else metrics_data.get("volume"),
            "difficulty": metrics_data.get("difficulty", {}).get("value") if isinstance(metrics_data.get("difficulty"), dict) else metrics_data.get("difficulty"),
            "results": metrics_data.get("results", {}).get("value") if isinstance(metrics_data.get("results"), dict) else metrics_data.get("results"),
            "brand": metrics_data.get("brand", {}).get("value") if isinstance(metrics_data.get("brand"), dict) else metrics_data.get("brand"),
            "max_reach": metrics_data.get("all_installs", {}).get("value") if isinstance(metrics_data.get("all_installs"), dict) else metrics_data.get("all_installs"),
        }
    
    return metrics_map


def fetch_all_gap_metrics(
    gap_terms: List[Dict[str, Any]],
    platform: str = "ios",
    country: str = "us",
    language: str = "us",
    device: str = "iphone",
    max_terms: int = 50,
) -> List[Dict[str, Any]]:
    """
    Fetch metrics for all gap terms, batched in groups of 5.
    
    Caps at max_terms to avoid excessive API calls.
    """
    # Cap at top N terms
    terms_to_fetch = gap_terms[:max_terms]
    skipped = len(gap_terms) - len(terms_to_fetch)
    
    if skipped > 0:
        print(f"[METRICS] Capping at {max_terms} terms, skipping {skipped}")
    
    # Extract term strings
    keywords = [t["term"] for t in terms_to_fetch]
    
    # Fetch in batches of 5
    all_metrics = {}
    batch_size = 5
    
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i : i + batch_size]
        print(f"[METRICS] Batch {i // batch_size + 1} ({i + 1}-{min(i + batch_size, len(keywords))}/{len(keywords)})")
        
        try:
            batch_metrics = fetch_keyword_metrics(
                batch,
                platform=platform,
                country=country,
                language=language,
                device=device,
            )
            all_metrics.update(batch_metrics)
        except Exception as e:
            print(f"[METRICS] Error fetching batch: {e}")
            # Mark as unavailable
            for kw in batch:
                all_metrics[kw] = {
                    "volume": None,
                    "difficulty": None,
                    "results": None,
                    "brand": None,
                    "max_reach": None,
                }
        
        # Sleep between batches (be respectful to API)
        if i + batch_size < len(keywords):
            time.sleep(0.5)
    
    # Enrich gap terms with metrics
    enriched_gaps = []
    for gap in terms_to_fetch:
        term = gap["term"]
        metrics = all_metrics.get(term, {
            "volume": None,
            "difficulty": None,
            "results": None,
            "brand": None,
            "max_reach": None,
        })
        
        enriched_gap = {
            "term": term,
            "primary_competitor_count": gap["primary_competitor_count"],
            "secondary_competitor_count": gap["secondary_competitor_count"],
            "volume": metrics.get("volume"),
            "difficulty": metrics.get("difficulty"),
            "results": metrics.get("results"),
            "brand": metrics.get("brand"),
            "max_reach": metrics.get("max_reach"),
        }
        enriched_gaps.append(enriched_gap)
    
    return enriched_gaps


# TODO: fetch keyword history for velocity scoring
# This would require calling the historical keyword metrics endpoint
# and computing volume trends over the 90-day window for ranking velocity.
