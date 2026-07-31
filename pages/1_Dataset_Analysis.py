"""
1_Dataset_Analysis.py

Dataset Analysis page for the DX Usage Intelligence Dashboard.

Shows dataset distribution across domains, providers, dataset
types, and access policies, plus a city-level breakdown table
and chart, sourced from the most recent snapshot.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import load_latest_snapshot
from theme import apply_theme
from dashboard_components import hero, metric_card, section, info_card, style_chart

st.set_page_config(
    page_title="Dataset Analysis",
    page_icon="📊",
    layout="wide"
)
apply_theme()

data = load_latest_snapshot()

if not data:
    st.error("No snapshot data available")
    st.stop()

# -------------------------------------------------------------------
# Build DataFrames from the snapshot
#
# Uses data.get(key, []) instead of data[key] when building these
# frames. Older snapshots (from before a field was added to the
# schema, or if a field is briefly empty because Elasticsearch
# returned no buckets for it) would otherwise raise a KeyError and
# crash the whole page instead of just showing an empty section.
# -------------------------------------------------------------------

domains_df = pd.DataFrame(data.get("domains", [])).sort_values(by="count", ascending=False)
providers_df = pd.DataFrame(data.get("providers", [])).sort_values(by="count", ascending=False)
dataset_types_df = pd.DataFrame(data.get("dataset_types", []))
access_df = pd.DataFrame(data.get("access_policies", []))

display_domains = domains_df.head(10).copy()
# Insert a line break in this one long domain label so it doesn't
# overflow the chart's y-axis label area.
display_domains["display_name"] = display_domains["name"].replace(
    {"environmental monitoring": "environmental<br>monitoring"}
)

timestamp = datetime.fromisoformat(data["timestamp"])
formatted_time = timestamp.strftime("%d %b %Y , %I:%M %p UTC")

hero(
    "📊 Dataset Analysis",
    f"Explore domains,providers,dataset types and access policies.\n\nLast Updated: {formatted_time}"
)

# -------------------------------------------------------------------
# Headline KPI cards
# -------------------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Domains", len(domains_df), "🌍")

with c2:
    metric_card("Providers", len(providers_df), "🏢")

with c3:
    metric_card("Dataset Types", len(dataset_types_df), "📊")

with c4:
    # Uses a safe "next() with a default" pattern (same as Home.py)
    # instead of access_df.loc[...].values[0], which raised an
    # IndexError if there was ever no row named exactly "open" (e.g.
    # every dataset happened to be restricted/private in a given
    # snapshot, or the access-policy field was briefly empty). A
    # missing "open" bucket now shows 0 instead of crashing the page.
    open_count = next(
        (row["count"] for _, row in access_df.iterrows() if row["name"] == "open"),
        0,
    )
    open_percentage = (
        (open_count / data["total_datasets"]) * 100
        if data.get("total_datasets")
        else 0
    )
    metric_card("Open Datasets", f"{open_count:,}", "🔓", f"{open_percentage:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Charts: domains, providers, dataset type, access policy
# -------------------------------------------------------------------

left, right = st.columns(2)

with left:
    section("Top 10 Domains")
    fig = px.bar(
        display_domains,
        x="count",
        y="display_name",
        orientation="h",
        text="count"
    )
    fig.update_yaxes(title="Name")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=90, t=20, b=10))
    fig.update_traces(marker_color="#2F6690")
    fig.update_traces(
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Datasets: %{x}<extra></extra>",
        cliponaxis=False,
        customdata=display_domains["name"]
    )
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Top 10 Providers")
    top_providers = providers_df.head(10)
    fig = px.bar(
        top_providers,
        x="count",
        y="name",
        orientation="h",
        text="count"
    )
    fig.update_traces(marker_color="#2F6690")
    fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=20, b=10))
    fig.update_traces(textposition='outside', hovertemplate="<b>%{y}</b><br>Datasets: %{x}<extra></extra>")
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    section("Dataset Type Distribution")
    fig = px.pie(
        dataset_types_df,
        names="name",
        values="count",
        color_discrete_sequence=["#12355B", "#2F6690", "#6FA8DC", "#8FBCE6", "#B7D4F2"]
    )
    fig.update_traces(textposition="inside", textfont=dict(size=13), marker=dict(line=dict(color="white", width=2)))
    fig.update_traces(textinfo="label+value+percent")
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Access Policy Distribution")
    fig = px.pie(
        access_df,
        names="name",
        values="count",
        color_discrete_sequence=["#12355B", "#2F6690", "#6FA8DC", "#8FBCE6", "#B7D4F2"]
    )
    fig.update_traces(textposition="inside", textfont=dict(size=13), marker=dict(line=dict(color="white", width=2)))
    fig.update_traces(textinfo="label+value+percent")
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.divider()

# -------------------------------------------------------------------
# Key Insights
#
# Guards against a genuinely empty snapshot (e.g. zero domains,
# providers, or dataset types during initial testing against a blank
# index). Reading .iloc[0] directly would raise an IndexError in that
# case, so each lookup falls back to a placeholder row, the same way
# largest_domain/largest_provider are guarded on the Home page.
# -------------------------------------------------------------------

section("Key Insights")

top_domain = (
    domains_df.iloc[0]
    if not domains_df.empty
    else {"name": "N/A", "count": 0}
)

top_provider = (
    providers_df.iloc[0]
    if not providers_df.empty
    else {"name": "N/A", "count": 0}
)

top_dataset_type = (
    dataset_types_df.sort_values("count", ascending=False).iloc[0]
    if not dataset_types_df.empty
    else {"name": "N/A", "count": 0}
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    info_card(
        "🌍 Largest Domain",
        f"{top_domain['name'].title()} ({top_domain['count']:,} datasets)"
    )

with c2:
    info_card(
        "🏢 Largest Provider",
        f"{top_provider['name'].title()} ({top_provider['count']:,} datasets)"
    )

with c3:
    info_card(
        "🔓 Open Datasets",
        f"{open_percentage:.1f}% of all datasets"
    )

with c4:
    info_card(
        "📊 Most Common Dataset Type",
        f"{top_dataset_type['name'].replace('adex:', '').title()} ({top_dataset_type['count']:,})"
    )

st.divider()

# -------------------------------------------------------------------
# Detailed statistics — full domain / provider tables
# -------------------------------------------------------------------

section("Detailed Statistics")
st.caption("Expand the sections below to view complete statistics.")
domain_table = domains_df.rename(columns={"name": "Domain", "count": "Datasets"})
provider_table = providers_df.rename(columns={"name": "Provider", "count": "Datasets"})

with st.expander("🌍 View All Domains"):
    st.dataframe(
        domain_table, use_container_width=True, hide_index=True,
        column_config={
            "Domain": st.column_config.TextColumn("Domain", width="large"),
            "Datasets": st.column_config.NumberColumn("Datasets", format="%d"),
        },
    )

with st.expander("🏢 View All Providers"):
    st.dataframe(
        provider_table, use_container_width=True, hide_index=True,
        column_config={
            "Provider": st.column_config.TextColumn("Provider", width="large"),
            "Datasets": st.column_config.NumberColumn("Datasets", format="%d"),
        },
    )

# -------------------------------------------------------------------
# City / instance breakdown
#
# Uses data.get("cities", []). Same reasoning as the domains/providers
# frames above — "cities" is a newer field, so any older snapshot that
# predates it would otherwise crash this page.
# -------------------------------------------------------------------

city_table = (
    pd.DataFrame(data.get("cities", []))
      .rename(columns={
          "name": "City / Instance",
          "count": "Datasets"
      })
      .sort_values("Datasets", ascending=False)
)

section("🏙️ Top 5 Cities")

if city_table.empty:
    st.info("No city-level data available in this snapshot yet.")
else:
    st.dataframe(
        city_table.head(5),
        use_container_width=True,
        hide_index=True,
        column_config={
            "City / Instance": st.column_config.TextColumn("City / Instance", width="large"),
            "Datasets": st.column_config.NumberColumn("Datasets", format="%d"),
        },
    )

    fig = px.bar(
        city_table.head(5),
        x="Datasets",
        y="City / Instance",
        orientation="h",
        text="Datasets"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=10, t=10, b=10)
    )

    fig.update_traces(
        marker_color="#2F6690",
        textposition="outside"
    )

    fig = style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

st.divider()
st.caption("Data source: IUDX Data Exchange. Data is updated periodically.")
