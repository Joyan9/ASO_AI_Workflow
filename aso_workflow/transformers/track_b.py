"""
Track B Transformation — Android A/B test history analysis

This module transforms raw metadata history for Android competitors into:
1. Filtered changes (title, short_description, icon, screenshots only)
2. Separated A/B tests vs shipped changes
3. Resolved A/B tests (won, lost, pending)
4. Per-competitor summaries

No API calls in this step — pure transformation from raw files.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import config


def _get_screenshot_ids(value: Any) -> List[str]:
    """Extract stable IDs from screenshots/icon value (list of objects with 'id' field)."""
    if not isinstance(value, list):
        return []
    return [item.get("id", "") for item in value if isinstance(item, dict)]


def _values_equal(target: str, old_val: Any, new_val: Any) -> bool:
    """
    Compare two values, with special handling for screenshots and icon.
    
    For screenshots/icon: compare by ID list (stable identifier).
    For everything else: exact string comparison.
    """
    if target in ("screenshots", "icon"):
        old_ids = _get_screenshot_ids(old_val)
        new_ids = _get_screenshot_ids(new_val)
        return old_ids == new_ids
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


def transform_track_b(app_id: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Main Track B transformation for Android A/B test history.
    
    Args:
        app_id: Android app ID (package name)
    
    Returns:
        (list of competitor dicts with ab_tests, shipped_changes, summary)
    """
    print("[TRACK_B] Loading competitor list...")
    
    # Load competitor list
    competitors_files = list(Path(config.DATA_RAW_DIR).glob("android_*_competitors.json"))
    
    if not competitors_files:
        print(f"[ERROR] No competitor list found for Android")
        return [], {}
    
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
    
    return output, {
        "total_competitors": len(output),
        "total_ab_tests": total_ab_tests,
        "resolved_won": total_resolved_won,
        "resolved_lost": total_resolved_lost,
        "pending": total_pending,
    }
