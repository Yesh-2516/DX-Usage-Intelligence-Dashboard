"""
utils.py

Provides utility functions for loading and caching dashboard
snapshot data. These helpers are used throughout the Streamlit
application to access the latest snapshot and historical records.
"""

import json
import streamlit as st
from config import SNAPSHOTS_DIR

# How long a cached snapshot read is considered "fresh", in seconds.
# The scheduler writes a new snapshot every run, so without a TTL the
# cache would keep serving the very first snapshot it ever loaded for
# the lifetime of the Streamlit process, regardless of new files
# appearing on disk. 300s = 5 minutes is a reasonable balance between
# "reasonably live" and "not re-reading disk on every rerun".
SNAPSHOT_CACHE_TTL = 300


def get_snapshot_files():
    """
    Retrieve all snapshot files sorted chronologically.
    Returns:
        list[Path]: Sorted list of snapshot JSON files.
    """
    return sorted(SNAPSHOTS_DIR.glob("*.json"))


def _load_snapshot(filepath):
    """
    Load a snapshot JSON file.
    Args:
        filepath (Path): Path to the snapshot file.
    Returns:
        dict: Snapshot contents.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# Uses ttl=SNAPSHOT_CACHE_TTL. Without a ttl, st.cache_data caches this
# for the lifetime of the Streamlit server process. Once the scheduler
# starts writing new snapshots in the background, the dashboard would
# otherwise keep showing the very first snapshot it loaded until the
# app was manually restarted.
@st.cache_data(show_spinner=False, ttl=SNAPSHOT_CACHE_TTL)
def load_latest_snapshot():
    """
    Load the most recent dashboard snapshot.
    Returns:
        dict | None: Latest snapshot if available,
        otherwise None.
    """
    files = get_snapshot_files()

    if not files:
        return None

    return _load_snapshot(files[-1])


# Uses ttl=SNAPSHOT_CACHE_TTL (see note above).
@st.cache_data(show_spinner=False, ttl=SNAPSHOT_CACHE_TTL)
def load_snapshot_history():
    """
    Load all available dashboard snapshots.
    Returns:
        list[dict]: List of snapshots ordered chronologically.
    """
    return [_load_snapshot(file) for file in get_snapshot_files()]
