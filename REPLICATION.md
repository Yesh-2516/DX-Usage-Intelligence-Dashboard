# Replication Playbook

## DX Usage Intelligence Dashboard

### Overview

The DX Usage Intelligence Dashboard was designed to be reusable across
different Data Exchange (DX) deployments. The architecture separates
data collection, snapshot storage, analytics, and visualization, making
it easy to adapt to another deployment with minimal code changes.

---

# Current Deployment

Current implementation targets the IUDX Data Exchange.

Data sources include:

- Elasticsearch
- Keycloak

The dashboard periodically collects metadata, generates snapshots,
detects changes, and presents analytics through a Streamlit interface.

---

# Components That Can Be Reused

The following modules are deployment-independent and can be reused
without modification.

- dashboard_components.py
- theme.py
- assistant.py
- utils.py
- delta_detector.py
- alert_manager.py
- Home.py
- Dataset Analysis page
- Trends page
- AI Assistant page

---

# Components That Require Configuration

When adapting the dashboard to another DX deployment,
only a few configuration files need modification.

## Elasticsearch

Update:

- ES_URL
- Authentication credentials
- Index names
- Aggregation queries (if metadata schema differs)

Files:

- config.py
- es_queries.py

---

## Keycloak

Update:

- Keycloak URL
- Realm
- Client credentials or user credentials
- Authentication configuration

Files:

- config.py
- keycloak_module.py

---

# Snapshot Pipeline

The pipeline remains unchanged.

```
Elasticsearch
        │
Keycloak
        │
        ▼
    fetch.py
        │
        ▼
 JSON Snapshots
        │
        ▼
Delta Detection
        │
        ▼
 Dashboard
```

---

# Steps to Replicate

1. Configure Elasticsearch connection.
2. Configure Keycloak connection.
3. Verify aggregation queries.
4. Run fetch.py.
5. Generate snapshots.
6. Launch the Streamlit dashboard.
7. Verify dashboard metrics.

---

# Supported Data Exchanges

The same architecture can be applied to:

- MahaAgX
- KrishiSetu
- TGDeX
- Other IUDX-compatible Data Exchanges

provided similar Elasticsearch metadata and authentication services are available.

---

# Future Extensions

Possible enhancements include:

- Additional metadata aggregations
- Deployment-specific dashboards
- Real-time streaming updates
- Email or Slack alert integration
- Multi-deployment dashboard support

---

# Conclusion

The dashboard follows a modular architecture in which
only deployment-specific configuration needs to change.
The snapshot pipeline, analytics engine, dashboard pages,
and AI Assistant can be reused across multiple Data Exchange
deployments with minimal modification.