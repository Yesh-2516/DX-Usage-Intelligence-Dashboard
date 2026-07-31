"""
alert_manager.py

Lightweight logging service for the DX Usage Intelligence Dashboard.
Captures delta changes between snapshots and writes them to a persistent log file.
"""

from pathlib import Path
from datetime import datetime, UTC

#Path to the alert log file
ALERT_FILE = Path(__file__).parent / "alerts.log"

#Log detected changes to alerts.log
"""Args: 
            changes (dict):Key-value pair of metric diffs from delta_detector.py
"""
def log_alert(changes):
    # Uses UTC to match the timestamps already used for snapshots
    # (fetch.py's get_timestamp() also uses datetime.now(UTC)) — keeps
    # alert log entries directly comparable to snapshot filenames
    # instead of mixing UTC and local server time.
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    with open(ALERT_FILE,"a") as f:
        f.write("="* 60 + "\n")
        f.write(f"Alert Time: {timestamp}\n\n")

        for key,value in changes.items():
            if value not in (None,"",[],{}):
                f.write(f"{key}: {value}\n")
        f.write("\n")