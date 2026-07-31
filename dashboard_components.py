"""
dashboard_components.py

Reusable Streamlit UI components used throughout the DX Usage
Intelligence Dashboard. These helpers provide consistent styling
for cards, headers, charts, chat messages, and other dashboard
elements.
"""

import streamlit as st


def hero(title: str, subtitle: str) -> None:
    """
    Display the dashboard hero section.

    Args:
        title (str): Dashboard title.
        subtitle (str): Short dashboard description.
    """
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h1 style="margin:0;">{title}</h1>
                    <p class="hero-text">{subtitle}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(
    title: str,
    value,
    icon: str | None = None,
    delta: str | None = None,
    delta_type: str = "positive",
) -> None:
    """
    Display a KPI metric card.

    Args:
        title (str): Metric title.
        value: Metric value.
        icon (str | None): Optional icon.
        delta (str | None): Change indicator.
        delta_type (str): Delta style.
    """
    delta_html = ""

    if delta is not None:
        delta_html = (
            f'<div class="metric-delta {delta_type}">{delta}</div>'
        )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon or ""}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-title">{title}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    """
    Display a section heading.

    Args:
        title (str): Section title.
    """
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def info_card(title: str, value) -> None:
    """
    Display an informational card.

    Args:
        title (str): Card heading.
        value: Card content.
    """
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">{title}</div>
            <div class="info-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def change_card(title: str, value, color: str = "#10B981") -> None:
    """
    Display a snapshot change card.

    Args:
        title (str): Change title.
        value: Change value.
        color (str): Reserved for future styling.
    """
    st.markdown(
        f"""
        <div class="change-card">
            <div class="change-title">{title}</div>
            <div class="change-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_card(status: bool = True) -> None:
    """
    Display the dashboard status indicator.

    Args:
        status (bool): Dashboard status.
    """
    colour = "#16A34A" if status else "#DC2626"
    text = "Live Snapshot" if status else "Offline"

    html = f"""
<div style="
background:white;
border-radius:20px;
padding:26px;
border-left:6px solid {colour};
box-shadow:0px 3px 12px rgba(0,0,0,0.05);
">

<h4 style="margin:0 0 12px 0;color:#12355B;">
Platform Status
</h4>

<div style="
color:{colour};
font-weight:700;
font-size:18px;
">
● {text}
</div>

</div>
"""

    st.markdown(html, unsafe_allow_html=True)


def footer() -> None:
    """
    Display the dashboard footer.
    """
    st.markdown(
        """
        <div class="footer">
            Powered by Elasticsearch • Keycloak •
            Streamlit • Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig):
    """
    Apply a consistent visual style to Plotly charts.

    Args:
        fig: Plotly figure.

    Returns:
        Plotly figure with dashboard styling.
    """
    fig.update_layout(
        template="plotly_white",
        title=dict(text=""),
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            size=14,
            color="#12355B",
        ),
        title_font=dict(
            size=18,
            color="#12355B",
        ),
        legend=dict(
            font=dict(
                size=13,
                color="#12355B",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
        height=420,
    )

    fig.update_xaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        tickfont=dict(
            size=12,
            color="#12355B",
        ),
        title_font=dict(
            size=13,
            color="#12355B",
        ),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
        tickfont=dict(
            size=12,
            color="#12355B",
        ),
        title_font=dict(
            size=13,
            color="#12355B",
        ),
    )

    return fig

def chat_bubble(role: str, message: str) -> None:
    """
    Display a chat message in the AI Assistant interface.
    Args:
        role (str): Either "user" or "assistant".
        message (str): Chat message.
    """
    if role == "user":
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-end; margin-bottom:16px;">
                <div style="
                    max-width:70%;
                    background:#DCEEFF;
                    border-radius:18px;
                    padding:16px 18px;
                    border:1px solid #C7DDF4;
                    box-shadow:0 2px 6px rgba(0,0,0,.05);
                ">
                    <div style="font-weight:600;color:#12355B;margin-bottom:8px;">
                        👤 You
                    </div>
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="
                background:white;
                border:1px solid #E5E7EB;
                border-radius:16px;
                padding:18px;
                margin-bottom:10px;">
                <b style="color:#12355B;">🤖 AI Assistant</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(message)