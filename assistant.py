"""
assistant.py

Implements the natural language query engine for the DX Usage
Intelligence Dashboard. Interprets user questions, identifies the 
requested dashboard category and intent, and returns data from the latest snapshot.
"""

import difflib

from delta_detector import get_latest_changes
from utils import load_latest_snapshot

# -------------------------------------------------------------------
# Dashboard Categories Configuration
# -------------------------------------------------------------------

CATEGORIES = {
    "provider": {
        "data_key": "providers",
        "total_key": "total_providers",
        "label": "provider",
        "plural": "providers",
        "unit": "datasets",
        "synonyms": ["provider", "providers"],
    },
    "domain": {
        "data_key": "domains",
        "total_key": "total_domains",
        "label": "domain",
        "plural": "domains",
        "unit": "datasets",
        "synonyms": ["domain", "domains"],
    },
    "city": {
        "data_key": "cities",
        "total_key": "total_cities",
        "label": "city",
        "plural": "cities",
        "unit": "datasets",
        "synonyms": ["city", "cities"],
    },
    "dataset_type": {
        "data_key": "dataset_types",
        "total_key": "total_dataset_types",
        "label": "dataset type",
        "plural": "dataset types",
        "unit": "datasets",
        "synonyms": [
            "dataset type",
            "dataset types",
            "type of dataset",
            "types of dataset",
        ],
    },
    "access_policy": {
        "data_key": "access_policies",
        "total_key": "total_access_policies",
        "label": "access policy",
        "plural": "access policies",
        "unit": "datasets",
        "synonyms": [
            "access policy",
            "access policies",
            "policy",
            "policies",
        ],
    },
}

# -------------------------------------------------------------------
# Supported User Intents & Suggested Questions
# -------------------------------------------------------------------

INTENT_WORDS = {
    "top": ["top", "show me the top", "rank", "ranking"],
    "largest": ["largest", "most", "highest", "biggest", "which has the most"],
    "smallest": ["smallest", "least", "lowest", "fewest"],
    "list": ["list", "show", "which", "what are", "available"],
    "count": ["how many", "count", "total", "number of"],
}

SUGGESTED_QUESTIONS = [
    "How many datasets are available?",
    "How many users are registered?",
    "Which provider has the most datasets?",
    "Which domain has the most datasets?",
    "How many open datasets are there?",
    "How many dataset types are available?",
    "List the domains",
    "What is the smallest provider?",
    "What has changed since the last snapshot?",
]

# -------------------------------------------------------------------
# Response Formatting Helpers
# -------------------------------------------------------------------

def top_items(title: str, items: list, n: int = 5) -> str:
    """Return the top N items sorted by dataset count."""
    if not items:
        return f"No items available for {title}."

    sorted_items = sorted(items, key=lambda x: x.get("count", 0), reverse=True)[:n]
    response = f"### Top {len(sorted_items)} {title}\n\n"

    for i, item in enumerate(sorted_items, start=1):
        name = item.get("name", "N/A").title()
        count = item.get("count", 0)
        response += f"{i}. {name} ({count:,} datasets)\n"

    return response


def largest_item(items: list) -> dict | None:
    """Return the item with the highest dataset count."""
    return max(items, key=lambda x: x.get("count", 0)) if items else None


def smallest_item(items: list) -> dict | None:
    """Return the item with the lowest dataset count."""
    return min(items, key=lambda x: x.get("count", 0)) if items else None


def list_items(title: str, items: list) -> str:
    """Format a complete list of items and their dataset counts."""
    if not items:
        return f"No {title.lower()} available."

    response = f"### {title}\n\n"
    for item in items:
        name = item.get("name", "N/A").title()
        count = item.get("count", 0)
        response += f"- {name} ({count:,} datasets)\n"

    return response


def format_changes(changes: dict) -> str:
    """Convert snapshot differences into a readable markdown response."""
    response = "### Changes Since Previous Snapshot\n\n"

    labels = {
        "dataset_growth": "Dataset count",
        "new_user_count": "User count",
        "new_domains": "New Domains",
        "new_providers": "New Providers",
        "new_cities": "New Cities",
        "new_dataset_types": "New Dataset Types",
        "new_access_policies": "New Access Policies",
    }

    has_content = False
    for key, label in labels.items():
        value = changes.get(key)
        if not value:
            continue

        has_content = True
        if isinstance(value, list):
            response += f"- {label}: {', '.join(value)}\n"
        else:
            sign = "+" if value > 0 else ""
            response += f"- {label}: {sign}{value}\n"

    if not has_content:
        response += "No changes detected."

    return response


# -------------------------------------------------------------------
# Question Interpretation
# -------------------------------------------------------------------

def detect_category(question: str) -> str | None:
    """Identify the dashboard category referenced in the user's question."""
    best_match = None
    best_len = 0

    for key, cfg in CATEGORIES.items():
        for synonym in cfg["synonyms"]:
            if synonym in question and len(synonym) > best_len:
                best_match = key
                best_len = len(synonym)

    return best_match


def detect_intent(question: str) -> str | None:
    """Determine the user's intent from the question."""
    for intent, phrases in INTENT_WORDS.items():
        if any(phrase in question for phrase in phrases):
            return intent
    return None


def answer_category_question(question: str, data: dict) -> str | None:
    """Generate a response for category-specific dashboard questions."""
    category = detect_category(question)
    if category is None:
        return None

    cfg = CATEGORIES[category]
    items = data.get(cfg["data_key"])
    if items is None:
        return None

    intent = detect_intent(question)
    has_counts = bool(items) and isinstance(items[0], dict) and "count" in items[0]

    if intent == "top" and has_counts:
        return top_items(cfg["plural"].title(), items)

    if intent == "largest":
        if has_counts:
            top = largest_item(items)
            return (
                f"**{top['name'].title()}** is the largest {cfg['label']} "
                f"with {top['count']:,} {cfg['unit']}."
            )
        return f"{cfg['label'].title()} data doesn't include counts to compare."

    if intent == "smallest":
        if has_counts:
            bottom = smallest_item(items)
            return (
                f"**{bottom['name'].title()}** is the smallest {cfg['label']} "
                f"with {bottom['count']:,} {cfg['unit']}."
            )
        return f"{cfg['label'].title()} data doesn't include counts to compare."

    if intent == "list":
        return list_items(cfg["plural"].title(), items)

    if intent == "count":
        total_key = cfg["total_key"]
        total_count = data.get(total_key, len(items))
        return f"There are currently **{total_count:,}** {cfg['plural']}."

    return list_items(cfg["plural"].title(), items)


# -------------------------------------------------------------------
# Fallback & Main Question Handling
# -------------------------------------------------------------------

def closest_suggestion(question: str) -> str | None:
    """Find the closest supported question using fuzzy matching."""
    mapping = {q.lower(): q for q in SUGGESTED_QUESTIONS}
    matches = difflib.get_close_matches(question, mapping.keys(), n=1, cutoff=0.4)
    return mapping[matches[0]] if matches else None


def fallback_message(question: str) -> str:
    """Generate a helpful fallback response for unsupported queries."""
    suggestion = closest_suggestion(question)
    lines = ["Sorry, I'm not able to answer that one yet."]

    if suggestion:
        lines.append(f"Did you mean: **{suggestion}**?")

    lines.append("\nHere is what I can currently help with:")
    for sug_q in SUGGESTED_QUESTIONS:
        lines.append(f"- {sug_q}")

    return "\n".join(lines)


def answer_question(question: str) -> str:
    """Main execution point for processing natural language queries."""
    data = load_latest_snapshot()
    if data is None:
        return "No snapshot data available."

    query = question.lower().strip()

    # 1. Open Datasets Query
    if "open" in query and ("dataset" in query or "how many" in query):
        for policy in data.get("access_policies", []):
            if policy.get("name", "").lower() == "open":
                return f"There are **{policy.get('count', 0):,}** open datasets."
    
    # 2. Total Datasets Query
    if "dataset" in query and any(w in query for w in ["how many", "count", "total", "number"]) and "type" not in query:
        return f"There are currently **{data.get('total_datasets', 0):,}** datasets available."

    # 3. Registered Users Query
    if "user" in query and any(w in query for w in ["how many", "count", "total", "registered"]):
        return f"There are currently **{data.get('user_count', 0):,}** registered users."

    # 4. Snapshot Delta Queries
    if any(w in query for w in ["change", "changed", "new", "delta", "update"]):
        changes = get_latest_changes()
        if changes is None:
            return "Not enough snapshots available for comparison."
        return format_changes(changes)

    # 5. Category Queries
    category_answer = answer_category_question(query, data)
    if category_answer is not None:
        return category_answer

    # 6. Fallback
    return fallback_message(query)