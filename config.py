"""
config.py

Loads configuration values from environment variables and defines
common project paths used throughout the dashboard application.

Environment variables include:
- Elasticsearch credentials
- Keycloak credentials
- Snapshot storage location
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# -------------------------------------------------------------------
# Project Directories
# -------------------------------------------------------------------

# Base directory of the project
BASE_DIR = Path(__file__).parent

# Directory where generated dashboard snapshots are stored
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

# Ensure the snapshots directory exists
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Elasticsearch Configuration
# -------------------------------------------------------------------

ES_URL = os.getenv("ES_URL")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")

# -------------------------------------------------------------------
# Keycloak Configuration
# -------------------------------------------------------------------

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")
USERNAME = os.getenv("KC_USERNAME")
PASSWORD = os.getenv("KC_PASSWORD")