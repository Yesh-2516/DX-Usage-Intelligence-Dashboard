"""
es_module.py

Provides helper functions for querying Elasticsearch and extracting
aggregated dashboard statistics used to generate snapshots.
"""

import requests

from config import ES_PASSWORD, ES_URL, ES_USERNAME
from es_queries import (
    ACCESS_POLICY_QUERY,
    DATASET_TYPE_QUERY,
    INDUSTRY_QUERY,
    LOCATION_QUERY,
    PROVIDER_QUERY,
)


def run_query(query: dict) -> dict | None:
    """
    Execute an Elasticsearch aggregation query.

    Args:
        query (dict): Elasticsearch query body.

    Returns:
        dict | None: JSON response if successful,
        otherwise None.
    """
    try:
        response = requests.post(
            f"{ES_URL.rstrip('/')}/iudx-v2__cat_v2/_search",
            json=query,
            auth=(ES_USERNAME, ES_PASSWORD),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("[ERROR] Elasticsearch request timed out.")

    except requests.exceptions.ConnectionError:
        print("[ERROR] Unable to connect to Elasticsearch.")

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Elasticsearch returned HTTP {e.response.status_code}.")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Elasticsearch request failed: {e}")

    except ValueError:
        print("[ERROR] Invalid JSON response from Elasticsearch.")

    return None


def extract_buckets(response: dict | None, aggregation_name: str) -> list:
    """
    Extract aggregation buckets from an Elasticsearch response.

    Args:
        response (dict | None): Elasticsearch response.
        aggregation_name (str): Aggregation name.

    Returns:
        list: List of dictionaries containing bucket names
        and document counts.
    """
    if not response:
        return []

    try:
        buckets = response["aggregations"][aggregation_name]["buckets"]

        return [
            {
                "name": bucket["key"],
                "count": bucket["doc_count"],
            }
            for bucket in buckets
        ]

    except (KeyError, TypeError):
        print(f"[ERROR] Missing aggregation: {aggregation_name}")
        return []


def extract_total_hits(response: dict | None) -> int:
    """
    Extract the total number of datasets from a search response.

    Args:
        response (dict | None): Elasticsearch response.

    Returns:
        int: Total dataset count.
    """
    if not response:
        return 0

    try:
        return response["hits"]["total"]["value"]

    except (KeyError, TypeError):
        print("[ERROR] Unable to determine total dataset count.")
        return 0


def fetch_paginated_data(
    index: str,
    query: dict,
    page: int = 0,
    page_size: int = 1000,
) -> dict:
    """
    Retrieve paginated search results from Elasticsearch.

    Not currently called by fetch_es_data() / the snapshot pipeline —
    kept here for scroll/pagination needs on larger indices, per the
    problem statement's "scroll or pagination for large ES result
    sets" requirement (Phase 2). Uses the same URL-building and
    error-handling pattern as run_query() so it's safe to wire in
    later without surprises.

    Args:
        index (str): Elasticsearch index.
        query (dict): Query body.
        page (int): Page number.
        page_size (int): Number of documents per page.

    Returns:
        dict: Elasticsearch response, or an empty dict on failure.
    """
    body = {
        **query,
        "from": page * page_size,
        "size": page_size,
    }

    try:
        response = requests.post(
            f"{ES_URL.rstrip('/')}/{index}/_search",
            auth=(ES_USERNAME, ES_PASSWORD),
            json=body,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Paginated Elasticsearch request failed: {e}")
        return {}


def fetch_es_data() -> dict:
    """
    Fetch all Elasticsearch statistics required by the dashboard.

    Returns:
        dict: Aggregated dashboard statistics.
    """
    print("[INFO] Fetching Elasticsearch data...")

    industry_response = run_query(INDUSTRY_QUERY)
    provider_response = run_query(PROVIDER_QUERY)
    access_policy_response = run_query(ACCESS_POLICY_QUERY)
    dataset_type_response = run_query(DATASET_TYPE_QUERY)
    location_response = run_query(LOCATION_QUERY)

    domains = extract_buckets(industry_response, "domains")
    providers = extract_buckets(provider_response, "providers")
    access_policies = extract_buckets(
        access_policy_response,
        "access_policies",
    )
    dataset_types = extract_buckets(
        dataset_type_response,
        "dataset_types",
    )
    cities = extract_buckets(location_response, "cities")

    total_datasets = extract_total_hits(industry_response)

    return {
        "domains": domains,
        "providers": providers,
        "cities": cities,
        "dataset_types": dataset_types,
        "access_policies": access_policies,
        "total_datasets": total_datasets,
        "total_domains": len(domains),
        "total_providers": len(providers),
        "total_dataset_types": len(dataset_types),
        "total_cities": len(cities),
    }