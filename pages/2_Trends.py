"""
2_Trends.py

Trends page for the DX Usage Intelligence Dashboard.

Shows dataset and user growth across the full snapshot history,
a latest-vs-previous comparison table, a recent snapshot history
table, and a summary of the most recent detected changes.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from delta_detector import get_latest_changes
from utils import load_snapshot_history
from theme import apply_theme
from dashboard_components import metric_card, style_chart

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")
apply_theme()

snapshots = load_snapshot_history()
history = []

for data in snapshots:
    history.append({
        "Timestamp": datetime.fromisoformat(data["timestamp"]),
        "Datasets": data.get("total_datasets"),
        "Users": data.get("user_count"),
        "Domains": data.get("total_domains"),
        "Providers": data.get("total_providers")
    })

history_df = pd.DataFrame(history)
history_df = history_df.sort_values("Timestamp")
changes = get_latest_changes()

if history_df.empty:
    st.warning("No snapshot history available yet.")
    st.stop()

latest = history_df.iloc[-1]
previous = history_df.iloc[-2] if len(history_df) > 1 else latest
formatted_time = latest["Timestamp"].strftime("%d %b %Y, %I:%M %p UTC")

st.title("📈 Trends")
st.caption("Monitor growth of datasets and registered users across snapshots")
st.caption(f"Last Updated: {formatted_time}")
st.divider()

# -------------------------------------------------------------------
# Headline KPI cards
# -------------------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Snapshots", len(history_df), "📂")

with c2:
    dataset_delta = int(latest["Datasets"] - previous["Datasets"])
    metric_card(
        "Latest Datasets", f"{int(latest['Datasets']):,}", "📦",
        f"▲ {dataset_delta:+}",
        "positive" if dataset_delta > 0 else "neutral"
    )

with c3:
    user_delta = latest["Users"] - previous["Users"]
    user_percent = (user_delta / previous["Users"] * 100 if previous["Users"] else 0)
    metric_card(
        "Latest Users",
        f"{int(latest['Users']):,}",
        "👤",
        f"▲ {user_delta:+} ({user_percent:.1f}%)",
        "positive" if user_delta > 0 else "neutral"
    )

with c4:
    metric_card("Domains", int(latest["Domains"]), "🌍")

st.divider()

# -------------------------------------------------------------------
# Growth charts
# -------------------------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Dataset Growth")
    fig = px.line(history_df, x="Timestamp", y="Datasets", markers=True)
    fig.layout.title = None
    fig.update_layout(title_text="")
    fig.update_traces(
        line=dict(color="#2F6690", width=3),
        marker=dict(size=7, color="#2F6690")
    )
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    st.subheader("User Growth")
    fig = px.line(history_df, x="Timestamp", y="Users", markers=True)
    fig.layout.title = None
    fig.update_layout(title_text="")
    fig.update_traces(
        line=dict(color="#2F6690", width=3),
        marker=dict(size=7, color="#2F6690")
    )
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("###")

# Guards against NaN when there's only one snapshot. .diff() on a
# single-row column produces one NaN value, so .mean() on that is
# also NaN, which would otherwise render as the literal text
# "nan/snapshot" on screen. Shows a friendly placeholder instead
# until there's enough history to compute a real average.
avg_dataset_growth = history_df["Datasets"].diff().mean()
avg_user_growth = history_df["Users"].diff().mean()

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Average Dataset Growth",
        f"{avg_dataset_growth:.1f}/snapshot" if pd.notna(avg_dataset_growth) else "Not enough data yet"
    )

with c2:
    st.metric(
        "Average User Growth",
        f"{avg_user_growth:.1f}/snapshot" if pd.notna(avg_user_growth) else "Not enough data yet"
    )

# -------------------------------------------------------------------
# Latest vs previous snapshot comparison table
# -------------------------------------------------------------------

st.subheader("📊 Latest vs Previous Snapshot")

comparison = pd.DataFrame({
    "Metric": [
        "Datasets",
        "Users",
        "Domains",
        "Providers"
    ],
    "Previous": [
        previous["Datasets"],
        previous["Users"],
        previous["Domains"],
        previous["Providers"]
    ],
    "Latest": [
        latest["Datasets"],
        latest["Users"],
        latest["Domains"],
        latest["Providers"]
    ]
})

# "Change" is computed exactly once, from the original numeric
# columns, before any string formatting happens. Computing it twice
# (once numerically, then again after .fillna("-") had already turned
# missing values into the string "-") would run a subtraction on
# string values and raise a TypeError if any metric was genuinely
# missing (NaN) in an older snapshot, crashing the page.
comparison["Change"] = comparison["Latest"] - comparison["Previous"]

comparison_display = comparison.copy()

comparison_display["Previous"] = comparison_display["Previous"].apply(
    lambda x: f"{int(x):,}" if pd.notna(x) else "-"
)

comparison_display["Latest"] = comparison_display["Latest"].apply(
    lambda x: f"{int(x):,}" if pd.notna(x) else "-"
)

# Guards with pd.notna(x) before int(x). int(nan) raises a
# ValueError, so any metric missing from an older snapshot would
# otherwise crash this formatting step. Missing changes display as
# "-" instead of crashing the page.
comparison_display["Change"] = comparison_display["Change"].apply(
    lambda x: (
        f"+{int(x):,}" if pd.notna(x) and x > 0
        else f"{int(x):,}" if pd.notna(x)
        else "-"
    )
)

st.dataframe(
    comparison_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Metric": st.column_config.TextColumn("Metric", width="medium"),
        "Previous": st.column_config.TextColumn("Previous"),
        "Latest": st.column_config.TextColumn("Latest"),
        "Change": st.column_config.TextColumn("Change"),
    },
)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Recent snapshot history table
# -------------------------------------------------------------------

st.subheader("📂 Snapshot History")
history_display = history_df.copy()
history_display["Timestamp"] = history_display["Timestamp"].dt.strftime("%d %b %Y %H:%M")
history_display = history_display.tail(10)
numeric = [
    "Datasets",
    "Users",
    "Domains",
    "Providers"
]

for col in numeric:
    history_display[col] = history_display[col].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "-"
    )

history_display = history_display.fillna("-")
st.dataframe(
    history_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
        "Datasets": st.column_config.TextColumn("Datasets"),
        "Users": st.column_config.TextColumn("Users"),
        "Domains": st.column_config.TextColumn("Domains"),
        "Providers": st.column_config.TextColumn("Providers"),
    },
)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Recent changes summary (from delta_detector)
# -------------------------------------------------------------------

st.subheader("📌 Recent Changes")

if changes:
    st.markdown(f"- 📦 **{changes['dataset_growth']}** datasets added since the previous snapshot.")
    st.markdown(f"- 👤 **{changes['new_user_count']}** new users registered.")
    st.markdown(f"- 🌍 **{len(changes['new_domains'])}** new domains detected.")
    st.markdown(f"- 🏢 **{len(changes['new_providers'])}** new providers added.")
    st.markdown(f"- 🏙️ **{len(changes['new_cities'])}** new cities added.")
else:
    st.info("Not enough snapshots available for comparison.")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Data Source: Elasticsearch and Keycloak snapshots.")
