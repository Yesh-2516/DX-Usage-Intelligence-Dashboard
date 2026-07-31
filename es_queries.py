"""
es_queries.py

Defines reusable Elasticsearch aggregation queries used by the snapshot generation pipeline to retrieve dashboard statistics.
"""

INDUSTRY_QUERY = {
    "size": 0,
    "track_total_hits": True,
    "aggs": {
        "domains": {
            "terms": {
                "field": "industry.keyword",
                "size": 100
            }
        }
    }
}

PROVIDER_QUERY = {
  "size": 0,
  "aggs": {
    "providers": {
      "terms": {
        "field": "organization.keyword",
        "size": 100
      }
    }
  }
}

ACCESS_POLICY_QUERY = {
  "size": 0,
  "aggs": {
    "access_policies": {
      "terms": {
        "field": "accessPolicy.keyword",
        "size": 100
      }
    }
  }
}

DATASET_TYPE_QUERY = {
  "size": 0,
    "aggs": {
        "dataset_types": {
        "terms": {
            "field": "type.keyword",
            "size": 100
        }
        }
    }
}

LOCATION_QUERY = {
  "size": 0,
  "aggs": {
    "cities": {
      "terms": {
        "field": "location.address.keyword",
        "size": 100
      }
    }
  }
}
