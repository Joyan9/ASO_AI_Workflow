"""
Track B Transformation — Android A/B test history analysis

This module transforms raw metadata history for Android competitors into:
1. Filtered changes (title, short_description, icon, screenshots only)
2. Separated A/B tests vs shipped changes
3. Resolved A/B tests (won, lost, pending) — with perceptual hashing for screenshots
4. Per-competitor summaries

No API calls in this step — pure transformation from raw files.
Screenshots are compared using perceptual hashing (pHash) to detect identical images
even when URLs differ due to AppTweak's URL rewriting.
"""

import json
import hashlib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
from io import BytesIO

try:
    from PIL import Image
    import imagehash
    HAS_IMAGE_LIBS = True
except ImportError:
    HAS_IMAGE_LIBS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import config


# Global hash cache to avoid re-downloading URLs
_PHASH_CACHE: Dict[str, str] = {}


def _get_screenshot_urls(value: Any) -> List[str]:
    """Extract URLs from screenshots/icon value (list of objects with 'url' field)."""
    if not isinstance(value, list):
        return []
    return [item.get("url", "") for item in value if isinstance(item, dict) and item.get("url")]


def _get_url_hash(url: str) -> Optional[str]:
    """
    Get URL-based hash for stable caching (MD5 of URL).
    """
    if not url:
        return None
    return hashlib.md5(url.encode()).hexdigest()


def _load_cached_phash(url_hash: str) -> Optional[str]:
    """Load perceptual hash from cache file if it exists."""
    cache_dir = Path(config.DATA_RAW_DIR) / "screenshot_hashes"
    cache_file = cache_dir / f"{url_hash}.txt"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                return f.read().strip()
        except Exception:
            return None
    
    return None


def _save_cached_phash(url_hash: str, phash: str) -> None:
    """Save perceptual hash to cache file."""
    cache_dir = Path(config.DATA_RAW_DIR) / "screenshot_hashes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = cache_dir / f"{url_hash}.txt"
    try:
        with open(cache_file, "w") as f:
            f.write(phash)
    except Exception as e:
        print(f"[WARN] Failed to cache phash for {url_hash}: {e}")


def _compute_phash(url: str) -> Optional[str]:
    """
    Download image from URL and compute perceptual hash.
    
    Returns:
        Perceptual hash string if successful, None otherwise
    """
    if not HAS_IMAGE_LIBS or not HAS_REQUESTS:
        return None
    
    # Check cache first
    url_hash = _get_url_hash(url)
    if url_hash and url_hash in _PHASH_CACHE:
        return _PHASH_CACHE[url_hash]
    
    cached_phash = _load_cached_phash(url_hash)
    if cached_phash:
        _PHASH_CACHE[url_hash] = cached_phash
        return cached_phash
    
    # Download image
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Load image and compute hash
        image = Image.open(BytesIO(response.content))
        phash = str(imagehash.phash(image))
        
        # Cache it
        _PHASH_CACHE[url_hash] = phash
        if url_hash:
            _save_cached_phash(url_hash, phash)
        
        return phash
        
    except Exception as e:
        print(f"[WARN] Failed to download/hash image {url}: {e}")
        return None


def _screenshot_sets_equal(old_urls: List[str], new_urls: List[str]) -> bool:
    """
    Compare two screenshot sets using perceptual hashes.
    
    Two screenshot sets are equal if all hashes match 1-to-1 (order-independent).
    Accounts for images that are identical but have different URLs.
    
    If hash computation fails, falls back to URL comparison.
    """
    if not HAS_IMAGE_LIBS:
        # Fallback: compare URLs directly if libraries not available
        print("[TRACK_B] imagehash/Pillow not installed, falling back to URL comparison")
        return sorted(old_urls) == sorted(new_urls)
    
    # Compute hashes for old and new
    old_hashes = set()
    new_hashes = set()
    fallback_to_urls = False
    
    for url in old_urls:
        phash = _compute_phash(url)
        if phash:
            old_hashes.add(phash)
        else:
            # Fallback: use URL if hash fails
            old_hashes.add(url)
            fallback_to_urls = True
    
    for url in new_urls:
        phash = _compute_phash(url)
        if phash:
            new_hashes.add(phash)
        else:
            # Fallback: use URL if hash fails
            new_hashes.add(url)
            fallback_to_urls = True
    
    if fallback_to_urls:
        print(f"[WARN] Hash computation failed for some screenshots, using URL comparison")
    
    return old_hashes == new_hashes


def _get_screenshot_ids(value: Any) -> List[str]:
    """Extract stable IDs from screenshots/icon value (list of objects with 'id' field)."""
    if not isinstance(value, list):
        return []
    return [item.get("id", "") for item in value if isinstance(item, dict)]


def _values_equal(target: str, old_val: Any, new_val: Any) -> bool:
    """
    Compare two values, with perceptual hashing for screenshots and icons.
    
    For screenshots/icon: download images, compute perceptual hashes, compare hash sets.
    For everything else: exact string comparison.
    
    Falls back to URL comparison if image download/hashing fails.
    """
    if target in ("screenshots", "icon"):
        # Use perceptual hashing for image comparison
        old_urls = _get_screenshot_urls(old_val)
        new_urls = _get_screenshot_urls(new_val)
        
        if not old_urls and not new_urls:
            return True
        if not old_urls or not new_urls:
            return False
        
        return _screenshot_sets_equal(old_urls, new_urls)
    else:
        return str(old_val) == str(new_val)


def _load_history(history_file: Path) -> Dict[str, Any]:
    """Load and parse a history JSON file."""
    try:
        with open(history_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {history_file.name}: {e}")
        return {}


def _filter_changes(changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter changes to keep only relevant fields.
    
    Keep only: title, short_description, icon, screenshots
    Drop: version, reviews, ratings, ranking, etc.
    """
    relevant_targets = {"title", "short_description", "icon", "screenshots"}
    return [c for c in changes if c.get("target") in relevant_targets]


def _separate_by_ab_test(changes: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    """
    Separate changes into A/B tests and shipped changes.
    
    A/B tests: is_ab_test == True
    Shipped: is_ab_test == False or None
    
    Both sorted by date (ascending).
    """
    ab_tests = []
    shipped_changes = []
    
    for change in changes:
        is_ab = change.get("is_ab_test")
        change_copy = change.copy()
        
        if is_ab is True:
            ab_tests.append(change_copy)
        else:
            shipped_changes.append(change_copy)
    
    # Sort by date ascending (chronological order)
    ab_tests.sort(key=lambda x: x.get("date", ""))
    shipped_changes.sort(key=lambda x: x.get("date", ""))
    
    return ab_tests, shipped_changes


def _resolve_ab_test(
    ab_test: Dict[str, Any],
    shipped_changes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Resolve a single A/B test against shipped changes.
    
    Logic:
    - Find later shipped changes for the SAME field/target
    - If later shipped value == test's new_value → "won"
    - If later shipped value == test's old_value → "lost"
    - No match → "pending"
    """
    test_target = ab_test.get("target")
    test_date = ab_test.get("date")
    test_old = ab_test.get("old_value")
    test_new = ab_test.get("new_value")
    
    resolved_entry = ab_test.copy()
    resolved_entry["resolved"] = "pending"
    
    # Find later shipped changes for the same target
    for shipped in shipped_changes:
        shipped_target = shipped.get("target")
        shipped_date = shipped.get("date")
        shipped_value = shipped.get("new_value")
        
        # Must be same field and later date
        if shipped_target != test_target or shipped_date <= test_date:
            continue
        
        # Compare values
        if _values_equal(test_target, shipped_value, test_new):
            resolved_entry["resolved"] = "won"
            resolved_entry["shipped_on"] = shipped_date
            return resolved_entry
        elif _values_equal(test_target, shipped_value, test_old):
            resolved_entry["resolved"] = "lost"
            resolved_entry["shipped_on"] = shipped_date
            return resolved_entry
    
    return resolved_entry


def _flatten_screenshot_array(value: Any) -> Optional[int]:
    """
    Convert screenshot/icon array to count of items.
    
    Returns None if empty, otherwise returns count.
    """
    if isinstance(value, list) and len(value) > 0:
        return len(value)
    return None


def _consolidate_tests_by_date_range(tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Consolidate identical consecutive tests into date ranges.
    
    Groups tests with identical target, old_value, and new_value into a single entry
    with a date_range instead of individual date entries.
    
    Returns list of consolidated tests.
    """
    if not tests:
        return []
    
    consolidated = []
    i = 0
    
    while i < len(tests):
        test = tests[i]
        
        # Create a comparison key (all fields except date/date_range/resolved)
        test_target = test.get("target")
        test_old_str = json.dumps(test.get("old_value"), sort_keys=True, default=str)
        test_new_str = json.dumps(test.get("new_value"), sort_keys=True, default=str)
        
        # Look ahead to find identical consecutive tests
        current_dates = [test.get("date")]
        j = i + 1
        
        while j < len(tests):
            next_test = tests[j]
            next_target = next_test.get("target")
            next_old_str = json.dumps(next_test.get("old_value"), sort_keys=True, default=str)
            next_new_str = json.dumps(next_test.get("new_value"), sort_keys=True, default=str)
            
            # Compare target and values
            if (next_target == test_target and 
                next_old_str == test_old_str and 
                next_new_str == test_new_str):
                current_dates.append(next_test.get("date"))
                j += 1
            else:
                break
        
        # Create consolidated test
        consolidated_test = test.copy()
        
        if len(current_dates) > 1:
            # Multiple identical tests - consolidate to date range
            consolidated_test["date_range"] = {
                "start": min(current_dates),
                "end": max(current_dates)
            }
            consolidated_test["test_cycle_count"] = len(current_dates)
        
        consolidated_test.pop("date", None)
        consolidated.append(consolidated_test)
        
        i = j
    
    return consolidated



def _optimize_test_structure(test: Dict[str, Any], text_variants: Dict[str, str]) -> Dict[str, Any]:
    """
    Optimize a single test's structure:
    1. Replace screenshot/icon arrays with counts
    2. Replace text values with variant references
    3. Remove redundant fields (version, is_ab_test always in ab_tests array)
    4. Remove null/empty values
    """
    optimized = {}
    
    for key, value in test.items():
        # Skip fields that provide no signal
        if key in ("version", "is_ab_test"):
            continue
        
        # Skip null values and empty objects
        if value is None:
            continue
        
        # Skip redundant "resolved" if it's pending (the default)
        if key == "resolved" and value == "pending":
            continue
        
        # Flatten screenshot/icon arrays to counts
        if key in ("old_value", "new_value"):
            parent_target = test.get("target")
            if parent_target in ("screenshots", "icon"):
                count = _flatten_screenshot_array(value)
                new_key = f"{key}_count"
                if count is not None:
                    optimized[new_key] = count
            elif parent_target in ("title", "short_description"):
                # Compress text values using variant dictionary
                if value:
                    text_str = str(value)
                    if text_str not in text_variants.values():
                        # Add new variant
                        variant_id = f"v{len(text_variants) + 1}"
                        text_variants[variant_id] = text_str
                    else:
                        # Find existing variant
                        variant_id = [k for k, v in text_variants.items() if v == text_str][0]
                    
                    optimized[f"{key}_ref"] = variant_id
            else:
                optimized[key] = value
        else:
            optimized[key] = value
    
    return optimized


def _optimize_output_structure(
    competitors: List[Dict[str, Any]],
    target_app: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, str]]:
    """
    Optimize the entire output structure:
    1. Consolidate tests by date range
    2. Flatten screenshot arrays
    3. Create text variants dictionary
    4. Remove empty shipped_changes
    5. Remove null/empty defaults
    """
    text_variants = {}
    
    optimized_competitors = []
    for competitor in competitors:
        optimized_comp = {
            "app_id": competitor["app_id"],
            "tier": competitor["tier"],
        }
        
        # Include name only if not null
        if competitor.get("name"):
            optimized_comp["name"] = competitor["name"]
        
        # Consolidate AB tests by date range
        ab_tests = competitor.get("ab_tests", [])
        consolidated_tests = _consolidate_tests_by_date_range(ab_tests)
        
        # Optimize each test
        optimized_tests = []
        for test in consolidated_tests:
            optimized_test = _optimize_test_structure(test, text_variants)
            optimized_tests.append(optimized_test)
        
        optimized_comp["ab_tests"] = optimized_tests
        
        # Include shipped_changes only if not empty
        shipped = competitor.get("shipped_changes", [])
        if shipped:
            optimized_shipped = []
            for change in shipped:
                optimized_change = _optimize_test_structure(change, text_variants)
                optimized_shipped.append(optimized_change)
            optimized_comp["shipped_changes"] = optimized_shipped
        
        # Include summary
        optimized_comp["summary"] = competitor.get("summary", {})
        
        optimized_competitors.append(optimized_comp)
    
    # Optimize target app
    optimized_target = {
        "title": target_app.get("title"),
        "short_description": target_app.get("short_description"),
        "summary": target_app.get("summary", {}),
    }
    
    # Include shipped_changes only if not empty
    shipped = target_app.get("shipped_changes", [])
    if shipped:
        optimized_shipped = []
        for change in shipped:
            optimized_change = _optimize_test_structure(change, text_variants)
            optimized_shipped.append(optimized_change)
        optimized_target["shipped_changes"] = optimized_shipped
    
    return optimized_target, optimized_competitors, text_variants


def _compute_summary(
    ab_tests_resolved: List[Dict[str, Any]],
    shipped_changes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute per-competitor summary stats."""
    summary = {
        "ab_tests_total": len(ab_tests_resolved),
        "resolved_won": len([t for t in ab_tests_resolved if t.get("resolved") == "won"]),
        "resolved_lost": len([t for t in ab_tests_resolved if t.get("resolved") == "lost"]),
        "pending": len([t for t in ab_tests_resolved if t.get("resolved") == "pending"]),
        "fields_tested": [],
        "most_recent_shipped": {},
    }
    
    # Unique fields tested
    fields_tested = set()
    for test in ab_tests_resolved:
        target = test.get("target")
        if target:
            fields_tested.add(target)
    summary["fields_tested"] = sorted(list(fields_tested))
    
    # Most recent shipped date per field
    field_dates = defaultdict(list)
    for shipped in shipped_changes:
        target = shipped.get("target")
        date = shipped.get("date")
        if target and date:
            field_dates[target].append(date)
    
    for field, dates in field_dates.items():
        summary["most_recent_shipped"][field] = max(dates)
    
    return summary


def _summarize_target_app(app_id: str) -> Dict[str, Any]:
    """
    Extract and summarize our target app's metadata and testing history.
    
    Args:
        app_id: Target app ID (Android package name)
    
    Returns:
        Dict with: title, short_description, ab_tests[], shipped_changes[], summary
        
    Returns empty dict if metadata or history not found.
    """
    target_app_info = {
        "title": None,
        "short_description": None,
        "shipped_changes": [],
        "summary": {
            "ab_tests_total": 0,
            "resolved_won": 0,
            "resolved_lost": 0,
            "pending": 0,
            "fields_tested": [],
            "most_recent_shipped": {},
        },
    }
    
    # Load metadata
    # /workspaces/ASO_AI_Workflow/aso_workflow/data/raw/android_com.tinder_metadata.json
    metadata_file = Path(config.DATA_RAW_DIR) / f"android_{app_id}_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            app_metadata = metadata.get("result", {}).get(app_id, {}).get("metadata", {})
            target_app_info["title"] = app_metadata.get("title")
            target_app_info["short_description"] = app_metadata.get("short_description")
    else:
        print(f"[WARN] No metadata found for target app at {metadata_file}")
    
    # Load history
    history_file = Path(config.DATA_RAW_DIR) / "our_app" / f"android_{app_id}_history.json"
    if not history_file.exists():
        print(f"[WARN] No history found for target app at {history_file}")
        return target_app_info
    
    history_data = _load_history(history_file)
    changes = history_data.get("result", {}).get(app_id, {}).get("changes", [])
    
    if not changes:
        print(f"[TRACK_B] Target app has no changes in history")
        return target_app_info
    
    # Filter to relevant fields
    filtered_changes = _filter_changes(changes)
    
    if not filtered_changes:
        print(f"[TRACK_B] Target app has no relevant changes in history")
        return target_app_info
    
    # Separate A/B tests and shipped
    ab_tests, shipped_changes = _separate_by_ab_test(filtered_changes)
    
    # Resolve A/B tests
    ab_tests_resolved = []
    for ab_test in ab_tests:
        resolved = _resolve_ab_test(ab_test, shipped_changes)
        ab_tests_resolved.append(resolved)
    
    # Compute summary
    summary = _compute_summary(ab_tests_resolved, shipped_changes)
    
    #target_app_info["ab_tests"] = ab_tests_resolved
    target_app_info["shipped_changes"] = shipped_changes
    target_app_info["summary"] = summary
    
    print(f"[TRACK_B] Target app: {target_app_info['title']}")
    print(f"    A/B tests: {summary['ab_tests_total']} (won: {summary['resolved_won']}, lost: {summary['resolved_lost']}, pending: {summary['pending']})")
    print(f"    Fields tested: {summary['fields_tested']}")
    print()
    
    return target_app_info


def transform_track_b(app_id: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Main Track B transformation for Android A/B test history.
    
    Args:
        app_id: Android app ID (package name)
    
    Returns:
        (target_app dict with metadata and testing history,
         list of competitor dicts with ab_tests, shipped_changes, summary,
         aggregate summary dict)
    """
    print("[TRACK_B] Summarizing target app...")
    target_app = _summarize_target_app(app_id)
    print()
    print("[TRACK_B] Loading competitor list...")
    
    # Load competitor list
    competitors_files = list(Path(config.DATA_RAW_DIR).glob("android_*_competitors.json"))
    
    if not competitors_files:
        print(f"[ERROR] No competitor list found for Android")
        return target_app, [], {}
    
    with open(competitors_files[0], "r") as f:
        competitors_data = json.load(f)
    
    competitors = competitors_data.get("competitors", [])
    competitors_by_id = {c["app_id"]: c for c in competitors}
    
    print(f"[TRACK_B] Found {len(competitors)} competitors")
    print()
    
    # Process each competitor
    competitors_dir = Path(config.DATA_RAW_DIR) / "competitors"
    output = []
    
    total_ab_tests = 0
    total_resolved_won = 0
    total_resolved_lost = 0
    total_pending = 0
    
    for idx, competitor in enumerate(competitors, 1):
        comp_id = competitor["app_id"]
        comp_tier = competitor["tier"]
        
        # Load history
        history_file = competitors_dir / f"android_{comp_id}_history.json"
        
        if not history_file.exists():
            print(f"[{idx}/{len(competitors)}] {comp_id} ({comp_tier}) — NO HISTORY FILE")
            print()
            continue
        
        history_data = _load_history(history_file)
        changes = history_data.get("result", {}).get(comp_id, {}).get("changes", [])
        
        if not changes:
            print(f"[{idx}/{len(competitors)}] {comp_id} ({comp_tier}) — NO CHANGES")
            print()
            continue
        
        # Filter to relevant fields
        filtered_changes = _filter_changes(changes)
        
        if not filtered_changes:
            print(f"[{idx}/{len(competitors)}] {comp_id} ({comp_tier}) — NO RELEVANT CHANGES")
            print()
            continue
        
        # Separate A/B tests and shipped
        ab_tests, shipped_changes = _separate_by_ab_test(filtered_changes)
        
        # Resolve A/B tests
        ab_tests_resolved = []
        for ab_test in ab_tests:
            resolved = _resolve_ab_test(ab_test, shipped_changes)
            ab_tests_resolved.append(resolved)
        
        # Compute summary
        summary = _compute_summary(ab_tests_resolved, shipped_changes)
        
        # Track totals
        total_ab_tests += summary["ab_tests_total"]
        total_resolved_won += summary["resolved_won"]
        total_resolved_lost += summary["resolved_lost"]
        total_pending += summary["pending"]
        
        # Get competitor name
        comp_name = None
        metadata_file = Path(config.DATA_RAW_DIR) / f"android_{comp_id}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                comp_name = metadata.get("result", {}).get(comp_id, {}).get("metadata", {}).get("title")
        
        # Build output entry
        entry = {
            "app_id": comp_id,
            "name": comp_name,
            "tier": comp_tier,
            "ab_tests": ab_tests_resolved,
            "shipped_changes": shipped_changes,
            "summary": summary,
        }
        
        output.append(entry)
        
        print(f"[{idx}/{len(competitors)}] {comp_id} ({comp_tier})")
        print(f"    A/B tests: {summary['ab_tests_total']} (won: {summary['resolved_won']}, lost: {summary['resolved_lost']}, pending: {summary['pending']})")
        print(f"    Fields tested: {summary['fields_tested']}")
        print()
    
    # Print summary
    print("=" * 60)
    print(f"Track B Summary")
    print("=" * 60)
    print(f"Total competitors processed: {len(output)}")
    print(f"Total A/B tests found: {total_ab_tests}")
    print(f"  - Won: {total_resolved_won}")
    print(f"  - Lost: {total_resolved_lost}")
    print(f"  - Pending: {total_pending}")
    print()
    
    # Apply optimizations to reduce token usage
    print("[TRACK_B] Applying output optimizations...")
    optimized_target, optimized_competitors, text_variants = _optimize_output_structure(output, target_app)
    print(f"    Created {len(text_variants)} text variants")
    print(f"    Consolidated date ranges across tests")
    print()
    
    return optimized_target, optimized_competitors, {
        "total_competitors": len(optimized_competitors),
        "total_ab_tests": total_ab_tests,
        "resolved_won": total_resolved_won,
        "resolved_lost": total_resolved_lost,
        "pending": total_pending,
        "text_variants": text_variants,
    }
