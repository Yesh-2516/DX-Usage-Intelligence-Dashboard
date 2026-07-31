"""
theme.py

Applies the custom visual theme for the DX Usage Intelligence Dashboard.
The stylesheet defines the appearance of dashboard components,charts,sidebar,chat interface and overall layout.
"""
import streamlit as st

def apply_theme():
    """
    Apply the dashboard's custom CSS theme.
    The stylesheet customizes Streamlit's default apperance to provide a consistent look and feel across all dashboard pages.
    """
    st.markdown( """
                <style>
                /* ------------ IMPORT FONT ------------ */
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                html, body, [class*="css"]{
                    font-family: 'Inter', sans-serif;
                }

                /* ------------ MAIN APP ------------ */
                .stApp{
                    background-color:#F8F6F1;
                    color:#1F2937;
                }

                .main .block-container{
                    padding-top: 0rem;
                    padding-bottom: 2rem;
                    max-width: 1280px;
                }

                /* ------------ HERO ------------ */
                .hero-card{
                    background:linear-gradient(135deg,#12355B,#2F6690);
                    border-radius:20px;
                    padding:42px 50px;
                    color:white;
                    box-shadow:0px 12px 30px rgba(0,0,0,0.15);
                    margin-bottom:25px;
                }

                .hero-card h1{
                    font-size:54px;
                    font-weight:800;
                    margin-bottom:14px;
                }

                .hero-text{
                    font-size:22px;
                    opacity:0.9;
                }

                /* ------------ KPI CARDS ------------ */
                .metric-card{
                    background:white;
                    border-radius:18px;
                    padding:14px;
                    border:1px solid #E6E6E6;
                    text-align:center;
                    transition:0.25s ease;
                    box-shadow:0px 3px 12px rgba(0,0,0,0.05);
                    min-height:145px;
                }

                .metric-card:hover{
                    transform:translateY(-3px);
                    box-shadow:0px 10px 22px rgba(0,0,0,0.10);
                }

                .metric-icon{
                    font-size:26px;
                    margin-top:6px;
                    margin-bottom:8px;
                }

                .metric-value{
                    font-size:38px;
                    font-weight:700;
                    color:#12355B;
                }

                .metric-title{
                    font-size:16px;
                    font-weight:600;
                    color:#6B7280;
                    margin-top:6px;
                }

                .metric-delta{
                    margin-top:10px;
                    font-size:0.85rem;
                    font-weight:600;
                    display:inline-block;
                    padding:5px 12px;
                    border-radius:999px;
                }

                .metric-delta.positive{
                    color:#22c55e;
                    background:rgba(34,197,94,.15);
                }

                .metric-delta.negative{
                    color:#ef4444;
                    background:rgba(239,68,68,.15);
                }

                .metric-delta.neutral{
                    color:#94a3b8;
                    background:rgba(148,163,184,.15);
                }
                
                /* ------------ SECTION TITLE ------------ */
                .section-title{
                    font-size:32px;
                    color:#12355B;
                    font-weight:700;
                    margin-top:32px;
                    margin-bottom:18px;
                }

                /* ------------ INFO CARD ------------- */
                .info-card{
                    background:white;
                    border-radius:20px;
                    padding:26px;
                    margin-bottom:15px;
                    border-left:6px solid #2F6690;
                    box-shadow:0px 3px 12px rgba(0,0,0,0.05);
                    transition:0.25s ease;
                }

                .info-card:hover{
                    transform:translateY(-3px);
                }

                .info-title{
                    color:#12355B;
                    font-weight:700;
                    font-size:20px;
                }

                .info-value{
                    margin-top:10px;
                    color:#374151;
                    font-size:17px;
                    line-height:1.7;
                }

                /* ---------- CHANGE CARD ---------- */
                .change-card{
                    background:#EEF7FF;
                    border-radius:16px;
                    padding:18px;
                    text-align:center;
                    border:1px solid #C9E5FF;
                    box-shadow:0px 3px 10px rgba(0,0,0,0.04);
                    transition:0.25s ease;
                }

                .change-title{
                    color:#6B7280;
                    font-size:15px;
                }

                .change-value{
                    color:#12355B;
                    font-size:32px;
                    font-weight:700;
                }

                /* ---------- PLOTLY ---------- */
                .js-plotly-plot{
                    border-radius:18px;
                    background:white;
                    padding:10px;
                    box-shadow:0px 3px 12px rgba(0,0,0,0.05);
                }

                /* ---------- STREAMLIT METRICS ---------- */
                div[data-testid="metric-container"]{
                    background:white;
                    border-radius:16px;
                    border:1px solid #ECECEC;
                    padding: 18px;
                    box-shadow:0px 3px 10px rgba(0,0,0,0.05);
                }      

                div[data-testid="metric-container"]:hover{
                    border:1px solid #2F6690;
                }

                /* ---------- BUTTON ---------- */
                .stButton>button{
                    background:#12355B;
                    color:white;
                    border:none;
                    border-radius:10px;
                    padding:10px 20px;
                }

                .stButton>button:hover{
                    background:#2F6690;
                    color:white;
                }

                /* ----------- EXPANDER ---------- */
                .streamlit-expanderHeader{
                    font-weight:600;
                    color:#12355B;
                }

                /* ----------- SIDEBAR ----------- */
                section[data-testid="stSidebar"]{
                    background:#FFFFFF;
                    border-right:1px solid #E5E7EB;
                    width:180px;
                    min-width:180px;
                    max-width:180px;
                }

                section[data-testid="stSidebar"] *{
                    color:#12355B;
                    font-size:16px;
                    font-weight:600;
                }

                section[data-testid="stSidebarNav"] a{
                    border-radius:10px;
                    padding:8px 10px;
                    margin-bottom:4px;
                }

                section[data-testid="stSidebarNav"] a:hover{
                    background:#EEF4FA;
                }

                section[data-testid="stSidebarNav"] *{
                    color:#12355B;
                }

                /* ----------- FOOTER ---------- */
                .footer{
                    text-align:center;
                    color:#7A7A7A;
                    margin-top:40px;
                    padding-top:20px;
                    border-top:1px solid #E5E7EB;
                    font-size:14px;
                    visibility:hidden;
                }

                header[data-testid="stHeader"]{
                    background:transparent;
                    height:0;
                }

                [data-testid="collapsedControl"]{
                    display: block !important;
                    visibility: visible !important;
                    position: fixed !important;
                    top: 10px !important;
                    left: 10px !important;
                    height: auto !important;
                    width: auto !important;
                    z-index: 9999 !important;
                }

                div[data-testid="stToolbar"]{
                    visibility:hidden;
                    height:0;
                }

                #MainMenu{
                    visibility:hidden; }
                
                div[data-testid="stVerticalBlock"]{
                    gap:0.8rem;
                }

                /* ---------- STREAMLIT 1.56 METRIC FIX ---------- */
                div[data-testid="metric-container"] * {
                    color: #12355B !important;
                }

                div[data-testid="metric-container"] label {
                    color: #6B7280 !important;
                    font-size: 15px !important;
                    font-weight: 600 !important;
                }

                div[data-testid="metric-container"] [data-testid="stMetricValue"] {
                    color: #12355B !important;
                    font-size: 34px !important;
                    font-weight: 700 !important;
                }

                div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
                    color: #16A34A !important;
                    font-size: 16px !important;
                    font-weight: 600 !important;
                }

                /* ---------- CHAT INPUT ----------- */
                div[data-testid="stChatInput"]{
                    background:transparent;
                    padding:0;
                }

                div[data-testid="stChatInput"] > div{
                    background:transparent;
                    border:none;
                    box-shadow:none;
                }

                div[data-testid="stBottomBlockContainer"]{
                    background:transparent;
                }

                section[data-testid="stBottom"],
                section[data-testid="stBottom"] > div,
                div[data-testid="stBottomBlockContainer"],
                div[data-testid="stBottomBlockContainer"] > div{
                    background:#F8F6F1 !important;
                    border-radius:0 !important;
                    box-shadow:none !important;
                }

                section[data-testid="stBottom"]{
                    border-top:none !important;
                }

                div[data-testid="stChatInput"] textarea{
                    color:#12355B;
                    background:white;
                    border:1px solid #D1D5DB;
                    box-shadow:0 3px 12px rgba(0,0,0,.05);
                    padding:14px;
                }

                div[data-testid="stChatInput"] textarea::placeholder{
                    color:#6B7280;
                }

                div[data-testid="stChatInput"] button{
                    background:#12355B;
                    color:white;
                    border-radius:10px;
                }
                </style>
                """, unsafe_allow_html=True)
