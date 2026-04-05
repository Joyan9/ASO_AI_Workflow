"""
Track A Transformation — Extract terms and build keyword gap corpus

This module:
1. Extracts and weights terms from app metadata (unigrams, bigrams, trigrams)
2. Merges into a corpus with competitor tracking
3. Filters to gap terms (not in your app)
4. Removes branded/developer terms via fuzzy matching
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

import config


# Field weights for term extraction
FIELD_WEIGHTS = {
    "title": 5,
    "subtitle": 4,
    "short_description": 4,
    "promotional_text": 4,
    "description_excerpt": 3,  # First 250 chars of description
    "description_remainder": 1,  # Rest of description
}

DESCRIPTION_EXCERPT_LENGTH = 250
STOPWORDS = set(stopwords.words("english"))


def _clean_text(text: str) -> str:
    """Lowercase and strip HTML/special chars."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Lowercase
    text = text.lower()
    return text


def _extract_unigrams_and_bigrams(text: str) -> List[str]:
    """Tokenize text into unigrams, bigrams, and trigrams, remove stopwords."""
    if not text:
        return []
    
    # Remove punctuation and tokenize
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = word_tokenize(text)
    
    # Filter stopwords
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    
    terms = []
    
    # Unigrams
    terms.extend(tokens)
    
    # Bigrams
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        terms.append(bigram)
    
    # Trigrams (3-word sequences)
    for i in range(len(tokens) - 2):
        trigram = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        terms.append(trigram)
    
    return terms


def _extract_app_terms(metadata: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
    """
    Extract terms from a single app's metadata.
    
    Returns list of dicts: [{"term": "...", "weight": N, "source_field": "..."}]
    """
    term_weights = {}  # term -> (weight, source_field)
    
    # Field extraction based on platform
    if platform.lower() == "ios":
        fields = {
            "title": metadata.get("title", ""),
            "subtitle": metadata.get("subtitle", ""),
            "promotional_text": metadata.get("promotional_text", ""),
            "description": metadata.get("description", ""),
        }
    elif platform.lower() == "android":
        fields = {
            "title": metadata.get("title", ""),
            "short_description": metadata.get("short_description", ""),
            "long_description": metadata.get("long_description", ""),
        }
    else:
        return []
    
    # Extract terms from each field
    for field_name, field_text in fields.items():
        if not field_text:
            continue
        
        field_text = _clean_text(field_text)
        
        # Special handling for description: split into excerpt and remainder
        if field_name == "description" or field_name == "long_description":
            excerpt = field_text[:DESCRIPTION_EXCERPT_LENGTH]
            remainder = field_text[DESCRIPTION_EXCERPT_LENGTH:]
            
            # Excerpt (weight 3)
            excerpt_weight = FIELD_WEIGHTS.get("description_excerpt", 3)
            for term in _extract_unigrams_and_bigrams(excerpt):
                if term not in term_weights or term_weights[term][0] < excerpt_weight:
                    term_weights[term] = (excerpt_weight, "description_excerpt")
            
            # Remainder (weight 1)
            remainder_weight = FIELD_WEIGHTS.get("description_remainder", 1)
            for term in _extract_unigrams_and_bigrams(remainder):
                if term not in term_weights or term_weights[term][0] < remainder_weight:
                    term_weights[term] = (remainder_weight, "description_remainder")
        else:
            # Regular field
            weight = FIELD_WEIGHTS.get(field_name, 1)
            for term in _extract_unigrams_and_bigrams(field_text):
                if term not in term_weights or term_weights[term][0] < weight:
                    term_weights[term] = (weight, field_name)
    
    # Convert to output format
    result = []
    for term, (weight, source_field) in term_weights.items():
        result.append({
            "term": term,
            "weight": weight,
            "source_field": source_field,
        })
    
    return result


def _build_corpus(
    your_app_id: str,
    your_app_metadata: Dict[str, Any],
    competitor_ids: List[str],
    competitor_metadata: Dict[str, Dict[str, Any]],
    platform: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Build a corpus merging all app terms.
    
    Returns dict of {term: {in_your_app, your_app_field, primary_count, secondary_count, source_apps, competitor_fields}}
    """
    corpus = defaultdict(lambda: {
        "in_your_app": False,
        "your_app_field": None,
        "primary_competitor_count": 0,
        "secondary_competitor_count": 0,
        "source_apps": [],
        "competitor_fields": set(),
    })
    
    # Extract your app terms
    your_terms = _extract_app_terms(your_app_metadata, platform)
    for term_data in your_terms:
        term = term_data["term"]
        corpus[term]["in_your_app"] = True
        corpus[term]["your_app_field"] = term_data["source_field"]
    
    # Load competitor details from raw competitors JSON
    raw_dir = Path(config.DATA_RAW_DIR)
    competitors_file = raw_dir / f"{platform}_{your_app_id}_competitors.json"
    
    competitors_by_id = {}
    if competitors_file.exists():
        with open(competitors_file, "r") as f:
            competitors_data = json.load(f)
            for comp in competitors_data["competitors"]:
                competitors_by_id[comp["app_id"]] = comp["tier"]
    
    # Extract competitor terms
    for comp_id in competitor_ids:
        comp_metadata = competitor_metadata.get(comp_id)
        if not comp_metadata:
            continue
        
        tier = competitors_by_id.get(comp_id, "secondary")
        comp_terms = _extract_app_terms(comp_metadata, platform)
        
        for term_data in comp_terms:
            term = term_data["term"]
            corpus[term]["source_apps"].append(comp_id)
            corpus[term]["competitor_fields"].add(term_data["source_field"])
            
            if tier == "primary":
                corpus[term]["primary_competitor_count"] += 1
            else:
                corpus[term]["secondary_competitor_count"] += 1
    
    # Convert sets to lists for JSON serialization
    for term in corpus:
        corpus[term]["competitor_fields"] = list(corpus[term]["competitor_fields"])
        corpus[term]["source_apps"] = list(set(corpus[term]["source_apps"]))
    
    return corpus


def _filter_gaps(corpus: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to gap terms (in_your_app = false).
    Sort by primary count DESC, then secondary count DESC.
    """
    gaps = [
        {
            "term": term,
            "primary_competitor_count": data["primary_competitor_count"],
            "secondary_competitor_count": data["secondary_competitor_count"],
            "source_apps": data["source_apps"],
            "competitor_fields": data["competitor_fields"],
        }
        for term, data in corpus.items()
        if not data["in_your_app"]
    ]
    
    # Sort
    gaps.sort(
        key=lambda x: (
            -x["primary_competitor_count"],
            -x["secondary_competitor_count"],
        )
    )
    
    return gaps


def _remove_branded_terms(
    gaps: List[Dict[str, Any]],
    your_app_metadata: Dict[str, Any],
    competitor_metadata: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Drop any term that matches app names or developer names via substring match.
    """
    # Collect all app and developer names
    names_to_remove = set()
    
    # Your app name
    names_to_remove.add(your_app_metadata.get("title", "").lower())
    
    # Developer name
    dev = your_app_metadata.get("developer", {})
    if isinstance(dev, dict):
        names_to_remove.add(dev.get("name", "").lower())
    
    # Competitor names and developers
    for comp_metadata in competitor_metadata.values():
        names_to_remove.add(comp_metadata.get("title", "").lower())
        dev = comp_metadata.get("developer", {})
        if isinstance(dev, dict):
            names_to_remove.add(dev.get("name", "").lower())
    
    # Filter out terms
    filtered_gaps = []
    for gap in gaps:
        term_lower = gap["term"].lower()
        is_branded = any(
            name_part in term_lower
            for name in names_to_remove
            for name_part in name.split()
            if len(name_part) > 2
        )
        
        if not is_branded:
            filtered_gaps.append(gap)
    
    return filtered_gaps


def generate_seeds(your_app_id: str, platform: str) -> List[str]:
    """
    Generate keyword seed list from n-gram extraction.
    
    Steps:
    1. Extract terms from your app and competitors
    2. Build corpus with competitor tracking
    3. Filter to gap terms (not in your app)
    4. Remove branded terms
    5. Cap at MAX_SEED_KEYWORDS
    6. Save seeds to JSON
    
    Returns:
        List of seed keywords (sorted by competitor presence)
    """
    print("\n[SEEDS] ========================================")
    print("[SEEDS] Step 1: Generate seed keywords")
    print("[SEEDS] ========================================")
    
    raw_dir = Path(config.DATA_RAW_DIR)
    comp_metadata_dir = raw_dir / "competitors"
    
    # Load your app metadata
    your_app_file = raw_dir / f"{platform}_{your_app_id}_metadata.json"
    with open(your_app_file, "r") as f:
        your_app_raw = json.load(f)
    
    your_app_metadata = your_app_raw["result"][str(your_app_id)]["metadata"]
    
    # Load competitor list
    competitors_file = raw_dir / f"{platform}_{your_app_id}_competitors.json"
    with open(competitors_file, "r") as f:
        competitors_data = json.load(f)
    
    competitor_ids = [c["app_id"] for c in competitors_data["competitors"]]
    
    # Load competitor metadata
    competitor_metadata = {}
    for comp_id in competitor_ids:
        comp_file = comp_metadata_dir / f"{platform}_{comp_id}_metadata.json"
        if comp_file.exists():
            with open(comp_file, "r") as f:
                comp_raw = json.load(f)
                comp_meta = comp_raw["result"].get(str(comp_id)) or comp_raw["result"].get(comp_id)
                if comp_meta:
                    competitor_metadata[comp_id] = comp_meta["metadata"]
    
    print(f"[SEEDS] Loaded metadata for {len(competitor_metadata)} competitors")
    
    # Extract and build corpus
    print("[SEEDS] Extracting terms...")
    corpus = _build_corpus(
        your_app_id=your_app_id,
        your_app_metadata=your_app_metadata,
        competitor_ids=competitor_ids,
        competitor_metadata=competitor_metadata,
        platform=platform,
    )
    print(f"[SEEDS] Built corpus with {len(corpus)} unique terms")
    
    # Filter to gaps
    print("[SEEDS] Filtering to gap terms...")
    gaps = _filter_gaps(corpus)
    print(f"[SEEDS] Found {len(gaps)} gap terms")
    
    # Remove branded terms
    print("[SEEDS] Removing branded terms...")
    gaps = _remove_branded_terms(gaps, your_app_metadata, competitor_metadata)
    print(f"[SEEDS] Retained {len(gaps)} after removing branded terms")
    
    # Cap at MAX_SEED_KEYWORDS
    capped_gaps = gaps[:config.MAX_SEED_KEYWORDS]
    if len(gaps) > len(capped_gaps):
        print(f"[SEEDS] Capped at {config.MAX_SEED_KEYWORDS} seeds (was {len(gaps)})")
    
    # Extract just the term strings
    seed_keywords = [gap["term"] for gap in capped_gaps]
    
    # Save seeds to JSON before making API calls
    output_dir = Path(config.DATA_RAW_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    seeds_file = output_dir / f"{platform}_{your_app_id}_keyword_seeds.json"
    seeds_output = {
        "meta": {
            "app_id": your_app_id,
            "platform": platform,
            "generated_at": datetime.now().isoformat(),
            "total_terms": len(gaps),
            "seeds_capped": len(seed_keywords),
        },
        "seeds": seed_keywords,
    }
    
    with open(seeds_file, "w") as f:
        json.dump(seeds_output, f, indent=2)
    
    print(f"[SEEDS] Saved {len(seed_keywords)} seeds to {seeds_file}")
    print()
    
    return seed_keywords


def compute_gaps_from_rankings(
    your_app_id: str,
    platform: str,
    ranking_responses: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Compute actual gaps from AppTweak ranking data.
    
    Takes merged ranking responses and computes:
    - A gap term is one where:
      - Your app: ranked = false (with fetch_performed = true)
      - At least 1 competitor: ranked = true
    
    Returns:
        (gap_list, your_app_summary)
    """
    print("\n[GAPS] ========================================")
    print("[GAPS] Step 2: Compute gaps from rankings")
    print("[GAPS] ========================================")
    
    raw_dir = Path(config.DATA_RAW_DIR)
    comp_metadata_dir = raw_dir / "competitors"
    
    # Load your app metadata for summary and competitor details
    your_app_file = raw_dir / f"{platform}_{your_app_id}_metadata.json"
    with open(your_app_file, "r") as f:
        your_app_raw = json.load(f)
    
    your_app_metadata = your_app_raw["result"][str(your_app_id)]["metadata"]
    
    # Load competitor list with tier info
    competitors_file = raw_dir / f"{platform}_{your_app_id}_competitors.json"
    with open(competitors_file, "r") as f:
        competitors_data = json.load(f)
    
    competitors_by_id = {c["app_id"]: c["tier"] for c in competitors_data["competitors"]}
    
    # Load competitor metadata for names
    competitor_metadata = {}
    for comp_id in competitors_by_id.keys():
        comp_file = comp_metadata_dir / f"{platform}_{comp_id}_metadata.json"
        if comp_file.exists():
            with open(comp_file, "r") as f:
                comp_raw = json.load(f)
                comp_meta = comp_raw["result"].get(str(comp_id)) or comp_raw["result"].get(comp_id)
                if comp_meta:
                    competitor_metadata[comp_id] = comp_meta["metadata"]
    
    # Process ranking data
    gaps = []
    
    for keyword_data in ranking_responses.get("keywords", []):
        term = keyword_data["term"]
        your_app_data = keyword_data["your_app"]
        competitors_data = keyword_data["competitors"]
        
        # A gap requires:
        # 1. Your app not ranked (rank = null, fetch_performed = true)
        # 2. At least one competitor ranked
        
        your_ranked = (
            your_app_data.get("ranked", False) and 
            your_app_data.get("fetch_performed", False)
        )
        
        # Check if we have valid your_app data (even if not ranked)
        if not your_app_data.get("fetch_performed", False):
            # Skip terms with no data for your app
            continue
        
        # Find ranked competitors
        ranked_competitors = [c for c in competitors_data if c.get("ranked", False)]
        
        if not your_ranked and len(ranked_competitors) > 0:
            # This is a gap!
            
            # Count by tier
            primary_count = sum(1 for c in ranked_competitors if c.get("tier") == "primary")
            secondary_count = sum(1 for c in ranked_competitors if c.get("tier") == "secondary")
            
            # Compute averages
            avg_rank = None
            avg_installs = None
            avg_relevancy = None
            avg_kei = None
            
            if ranked_competitors:
                ranks = [c.get("rank") for c in ranked_competitors if c.get("rank") is not None]
                if ranks:
                    avg_rank = sum(ranks) / len(ranks)
                
                installs = [c.get("installs") for c in ranked_competitors if c.get("installs") is not None]
                if installs:
                    avg_installs = sum(installs) / len(installs)
                
                relevancies = [c.get("relevancy") for c in ranked_competitors if c.get("relevancy") is not None]
                if relevancies:
                    avg_relevancy = sum(relevancies) / len(relevancies)
                
                keis = [c.get("kei") for c in ranked_competitors if c.get("kei") is not None]
                if keis:
                    avg_kei = sum(keis) / len(keis)
            
            gap_entry = {
                "term": term,
                "primary_competitor_count": primary_count,
                "secondary_competitor_count": secondary_count,
                "your_app_ranked": False,
                "top_competitor_rank": min([c.get("rank") for c in ranked_competitors if c.get("rank") is not None], default=None),
                "avg_rank": avg_rank,
                "avg_installs": avg_installs,
                "avg_relevancy": avg_relevancy,
                "avg_kei": avg_kei,
                "source_apps": [c["app_id"] for c in ranked_competitors],
            }
            
            gaps.append(gap_entry)
    
    # Sort by primary count, then secondary count
    gaps.sort(key=lambda x: (-x["primary_competitor_count"], -x["secondary_competitor_count"]))
    
    # Your app summary
    your_app_summary = {
        "title": your_app_metadata.get("title"),
        "subtitle": your_app_metadata.get("subtitle") or your_app_metadata.get("short_description"),
        "description_excerpt": (your_app_metadata.get("description") or your_app_metadata.get("long_description") or "")[:250],
    }
    
    print(f"[GAPS] Identified {len(gaps)} keyword gaps")
    print()
    
    return gaps, your_app_summary


def transform_track_a(
    your_app_id: str,
    platform: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    DEPRECATED: Use generate_seeds() and compute_gaps_from_rankings() instead.
    
    This function kept for backward compatibility only.
    """
    print("[TRANSFORM] Using legacy transform_track_a (deprecated)")
    print("[TRANSFORM] Use generate_seeds() and compute_gaps_from_rankings() for new flow")
    
    # Generate seeds and return as fallback
    seeds = generate_seeds(your_app_id, platform)
    
    # Create minimal gap entries for backward compatibility
    gaps = [{"term": seed} for seed in seeds]
    
    raw_dir = Path(config.DATA_RAW_DIR)
    your_app_file = raw_dir / f"{platform}_{your_app_id}_metadata.json"
    with open(your_app_file, "r") as f:
        your_app_raw = json.load(f)
    
    your_app_metadata = your_app_raw["result"][str(your_app_id)]["metadata"]
    
    your_app_summary = {
        "title": your_app_metadata.get("title"),
        "subtitle": your_app_metadata.get("subtitle") or your_app_metadata.get("short_description"),
        "description_excerpt": (your_app_metadata.get("description") or your_app_metadata.get("long_description") or "")[:250],
        "term_count": len(gaps),
    }
    
    return gaps, your_app_summary
