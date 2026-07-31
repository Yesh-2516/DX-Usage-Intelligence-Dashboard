"""
fetch.py

Generates dashboard snapshots by collecting data from
Elasticsearch and Keycloak, combining the results into a
single JSON snapshot, and saving it to the snapshots directory.

This script also runs delta detection and alerting immediately after
saving a new snapshot (see the end of main()). delta_detector.py only
logs an alert when it is run directly as its own script, and since
the scheduled job (cron / GitHub Actions) only calls fetch.py, this
ensures the scheduled pipeline runs the full
"fetch -> save -> compare -> alert" sequence end to end, as intended.
"""

from datetime import UTC, datetime
import json

from config import SNAPSHOTS_DIR
from es_module import fetch_es_data
from keycloak_module import fetch_keycloak_data
from delta_detector import get_latest_changes
from alert_manager import log_alert


def get_timestamp() -> str:
    """
    Generate the current UTC timestamp in ISO 8601 format.

    Returns:
        str: Current timestamp.
    """
    return datetime.now(UTC).isoformat()


def save_snapshot(data: dict) -> None:
    """
    Save a dashboard snapshot as a JSON file.

    The filename is derived from the snapshot timestamp, with
    colons replaced to ensure compatibility across operating systems.

    Args:
        data (dict): Snapshot data to be written.
    """
    filename = f"{data['timestamp'].replace(':', '-')}.json"
    filepath = SNAPSHOTS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[INFO] Snapshot saved successfully: {filepath}")


def run_delta_check_and_alert() -> None:
    """
    Compare the newly saved snapshot against the previous one and
    log an alert if any meaningful change is detected.

    This is the automated equivalent of manually running
    delta_detector.py after every fetch. Safe to call even when
    fewer than two snapshots exist yet (get_latest_changes()
    returns None in that case).
    """
    changes = get_latest_changes()

    if changes is None:
        print("[INFO] Not enough snapshots to run delta detection yet.")
        return

    # A numeric field (e.g. dataset_growth) of 0 is a real, meaningful
    # value (nothing changed) and should NOT be treated as "no data" -
    # only list/string fields being empty count as "nothing to report".
    has_changes = any(
        value != 0 if isinstance(value, int) else bool(value)
        for value in changes.values()
    )

    if has_changes:
        log_alert(changes)
        print("[INFO] Delta detected — alert logged to alerts.log.")
    else:
        print("[INFO] No meaningful changes detected since last snapshot.")


def main() -> None:
    """
    Generate and store a dashboard snapshot.

    The snapshot combines:
    - Elasticsearch metadata and aggregations
    - Keycloak user statistics

    If Keycloak is unavailable, snapshot generation continues
    using a default user count of zero.
    """
    print("[INFO] Starting dashboard snapshot generation...")

    # Fetch Elasticsearch data
    try:
        print("[INFO] Fetching Elasticsearch data...")
        es_data = fetch_es_data()
        print("[INFO] Elasticsearch data fetched successfully.")
    except Exception as e:
        print(f"[ERROR] Elasticsearch fetch failed: {e}")
        print("[ERROR] Snapshot generation aborted.")
        return

    # Fetch Keycloak data
    try:
        print("[INFO] Fetching Keycloak data...")
        keycloak_data = fetch_keycloak_data()
        print("[INFO] Keycloak data fetched successfully.")
    except Exception as e:
        print(f"[WARNING] Keycloak fetch failed: {e}")
        print("[WARNING] Continuing with user_count = 0")
        keycloak_data = {"user_count": 0}

    snapshot = {
        "timestamp": get_timestamp(),
        "domains": es_data["domains"],
        "providers": es_data["providers"],
        "cities": es_data["cities"],
        "dataset_types": es_data["dataset_types"],
        "access_policies": es_data["access_policies"],
        "user_count": keycloak_data.get("user_count", 0) or 0,
        "total_datasets": es_data["total_datasets"],
        "total_domains": es_data["total_domains"],
        "total_providers": es_data["total_providers"],
        "total_dataset_types": es_data["total_dataset_types"],
        "total_cities": es_data["total_cities"],
    }

    save_snapshot(snapshot)

    # Runs delta detection + alerting right after saving, so the
    # scheduled job handles the full pipeline automatically.
    run_delta_check_and_alert()

    print("[INFO] Dashboard snapshot generation completed successfully.")


if __name__ == "__main__":
    main()
