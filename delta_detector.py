"""
delta_detector.py

Compares the two most recent dashboard snapshots to identify
changes in datasets, providers, domains, cities, dataset types,
access policies, and registered users. If changes are detected,
they can be logged using the alert manager.
"""

import json
from alert_manager import log_alert
from config import SNAPSHOTS_DIR


def get_snapshot_files() -> list:
    """
    Retrieve all available snapshot files sorted chronologically.

    Returns:
        list[Path]: Sorted list of snapshot files.
    """
    return sorted(SNAPSHOTS_DIR.glob("*.json"))


def load_snapshot(filepath) -> dict:
    """
    Load a dashboard snapshot from disk.

    Args:
        filepath (Path): Snapshot file path.

    Returns:
        dict: Snapshot contents.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_snapshots(old_snapshot: dict, new_snapshot: dict) -> dict:
    """
    Compare two dashboard snapshots and identify changes.

    Args:
        old_snapshot (dict): Previous snapshot.
        new_snapshot (dict): Latest snapshot.

    Returns:
        dict: Dictionary containing detected additions and
        numerical changes between snapshots.
    """
    # Uses .get(key, []) instead of direct indexing (["domains"], etc.)
    # As the snapshot schema evolves (e.g. "cities" was added after the
    # pipeline had already been running), older snapshots on disk won't
    # have every key. Direct indexing would raise a KeyError the first
    # time an old snapshot without a newer field is compared. .get()
    # with a default treats "field didn't exist yet" the same as
    # "field was empty", which is the correct behaviour here.
    old_domains = {item["name"] for item in old_snapshot.get("domains", [])}
    new_domains = {item["name"] for item in new_snapshot.get("domains", [])}

    old_providers = {item["name"] for item in old_snapshot.get("providers", [])}
    new_providers = {item["name"] for item in new_snapshot.get("providers", [])}

    old_cities = {item["name"] for item in old_snapshot.get("cities", [])}
    new_cities = {item["name"] for item in new_snapshot.get("cities", [])}

    old_dataset_types = {
        item["name"] for item in old_snapshot.get("dataset_types", [])
    }
    new_dataset_types = {
        item["name"] for item in new_snapshot.get("dataset_types", [])
    }

    old_access = {
        item["name"] for item in old_snapshot.get("access_policies", [])
    }
    new_access = {
        item["name"] for item in new_snapshot.get("access_policies", [])
    }

    return {
        "new_domains": list(new_domains - old_domains),
        "new_providers": list(new_providers - old_providers),
        "new_cities": list(new_cities - old_cities),
        "new_dataset_types": list(
            new_dataset_types - old_dataset_types
        ),
        "new_access_policies": list(new_access - old_access),
        # .get(..., 0) is used on both old and new snapshots for
        # user_count, so a missing field is treated as 0 either way.
        "new_user_count": (
            new_snapshot.get("user_count", 0)
            - old_snapshot.get("user_count", 0)
        ),
        "dataset_growth": (
            new_snapshot.get("total_datasets", 0)
            - old_snapshot.get("total_datasets", 0)
        ),
    }


def get_latest_changes() -> dict | None:
    """
    Compare the two most recent dashboard snapshots.

    Returns:
        dict | None: Snapshot differences if at least two
        snapshots exist, otherwise None.
    """
    files = get_snapshot_files()

    if len(files) < 2:
        return None

    old_snapshot = load_snapshot(files[-2])
    new_snapshot = load_snapshot(files[-1])

    return compare_snapshots(old_snapshot, new_snapshot)


if __name__ == "__main__":
    changes = get_latest_changes()

    if changes is None:
        print("[INFO] Not enough snapshots to compare.")

    else:
        print(changes)

        # Log changes only when at least one difference exists.
        has_changes = any(
            bool(value) if not isinstance(value, int) else value != 0
            for value in changes.values()
        )

        if has_changes:
            log_alert(changes)
            print("[INFO] Alert logged successfully.")
        else:
            print("[INFO] No changes detected.")
