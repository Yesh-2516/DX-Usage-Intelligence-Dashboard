"""
keycloak_module.py

Provides helper functions for authenticating with Keycloak and
retrieving user statistics for the dashboard snapshot pipeline.
"""

import requests

from config import (
    CLIENT_ID,
    KEYCLOAK_URL,
    PASSWORD,
    REALM,
    USERNAME,
)


def get_access_token() -> str | None:
    """
    Authenticate with Keycloak and retrieve an access token.

    Returns:
        str | None: Access token if authentication succeeds,
        otherwise None.
    """
    url = (
        f"{KEYCLOAK_URL}/realms/{REALM}"
        "/protocol/openid-connect/token"
    )

    payload = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to obtain Keycloak token: {e}")
        return None

    except (KeyError, ValueError):
        print("[ERROR] Invalid Keycloak authentication response.")
        return None


def get_user_count() -> int | None:
    """
    Retrieve the total number of registered users from Keycloak.

    Returns:
        int | None: Number of users if successful,
        otherwise None.
    """
    token = get_access_token()

    if token is None:
        return None

    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/count"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        return int(response.text)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to retrieve Keycloak user count: {e}")
        return None

    except ValueError:
        print("[ERROR] Invalid user count returned by Keycloak.")
        return None


def fetch_keycloak_data() -> dict:
    """
    Fetch Keycloak statistics required by the dashboard.

    Returns:
        dict: Dictionary containing the total registered
        user count. If Keycloak is unavailable, the user
        count defaults to zero.
    """
    user_count = get_user_count()

    return {
        "user_count": user_count if user_count is not None else 0,
    }