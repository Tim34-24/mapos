"""
Injection des styles globaux MapOS
Charte visuelle : CrisisOS — dark mode, Inter, rouge #E24B4A
"""

import streamlit as st


def inject_styles():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>

    /* ── Reset & base ───────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif !important;
        background-color: #1C1C1A !important;
        color: #E8E6E1 !important;
    }

    /* Cache les éléments Streamlit par défaut */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Supprime le padding top Streamlit */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #202020 !important;
        border-right: 0.5px solid rgba(232,230,225,0.08) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem !important;
    }

    /* Logo MapOS */
    .mapos-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.25rem 0 0.5rem;
    }
    .logo-icon { font-size: 26px; }
    .logo-name {
        font-size: 18px;
        font-weight: 500;
        color: #E8E6E1;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .logo-sub {
        font-size: 11px;
        color: #7A7873;
        letter-spacing: 0.02em;
    }

    /* Divider sidebar */
    .sidebar-divider {
        height: 0.5px;
        background: rgba(232,230,225,0.08);
        margin: 0.75rem 0;
    }

    /* Labels de section nav */
    .nav-label {
        font-size: 10px;
        font-weight: 500;
        color: #A32D2D;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
        margin-top: 4px;
    }

    /* Boutons sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 0.5px solid transparent !important;
        color: #7A7873 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        text-align: left !important;
        padding: 7px 10px !important;
        border-radius: 8px !important;
        transition: all 0.15s !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(232,230,225,0.06) !important;
        color: #E8E6E1 !important;
        border-color: rgba(232,230,225,0.1) !important;
    }

    /* Texte vide sidebar */
    .sidebar-empty {
        font-size: 12px;
        color: #4A4946;
        line-height: 1.6;
        padding: 6px 4px;
    }
    .sidebar-empty b { color: #7A7873; }

    /* Version en bas */
    .sidebar-bottom { margin-top: 2rem; }
    .sidebar-version {
        font-size: 11px;
        color: #4A4946;
        text-align: center;
        padding: 4px 0;
    }

    /* ── Cards ───────────────────────────────────────────── */
    .mapos-card {
        background: #272724;
        border: 0.5px solid rgba(232,230,225,0.08);
        border-radius: 12px;
        padding: 1.25rem;
        transition: border-color 0.15s, transform 0.15s;
        margin-bottom: 12px;
    }
    .mapos-card:hover {
        border-color: rgba(232,230,225,0.2);
        transform: translateY(-2px);
    }
    .mapos-card-lg {
        background: #272724;
        border: 0.5px solid rgba(232,230,225,0.08);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 16px;
    }

    /* ── Titres ──────────────────────────────────────────── */
    .page-title {
        font-size: 22px;
        font-weight: 500;
        color: #E8E6E1;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 13px;
        color: #7A7873;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #E8E6E1;
        letter-spacing: -0.015em;
        margin-bottom: 8px;
    }
    .card-eyebrow {
        font-size: 10px;
        font-weight: 500;
        color: #A32D2D;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    /* ── Badges ──────────────────────────────────────────── */
    .badge {
        display: inline-block;
        font-size: 10px;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
        margin-right: 4px;
    }
    .badge-ok   { background: #0D2B1E; color: #5DCAA5; }
    .badge-warn { background: #2A1A05; color: #EF9F27; }
    .badge-err  { background: #2E1212; color: #F09595; }
    .badge-info { background: #0C2A3E; color: #85B7EB; }
    .badge-red  { background: #E24B4A; color: #FFFFFF; }

    /* ── Métriques ───────────────────────────────────────── */
    .metric-card {
        background: #272724;
        border: 0.5px solid rgba(232,230,225,0.08);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-label {
        font-size: 11px;
        color: #7A7873;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 500;
        color: #E8E6E1;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 11px;
        color: #4A4946;
        margin-top: 3px;
    }

    /* ── Inputs Streamlit ────────────────────────────────── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #1C1C1A !important;
        border: 0.5px solid rgba(232,230,225,0.08) !important;
        border-radius: 8px !important;
        color: #E8E6E1 !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(232,230,225,0.3) !important;
        box-shadow: none !important;
    }
    label, .stLabel {
        color: #7A7873 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* ── Boutons principaux ──────────────────────────────── */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: #E24B4A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 18px !important;
        transition: background 0.15s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #c93d3c !important;
    }
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #E8E6E1 !important;
        border: 0.5px solid rgba(232,230,225,0.2) !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 18px !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(232,230,225,0.06) !important;
        border-color: rgba(232,230,225,0.3) !important;
    }

    /* ── Progress bars ───────────────────────────────────── */
    .stProgress > div > div > div {
        background-color: #E24B4A !important;
    }
    .stProgress > div > div {
        background-color: rgba(232,230,225,0.08) !important;
        border-radius: 4px !important;
    }

    /* ── Alerts / info boxes ─────────────────────────────── */
    .stAlert {
        background: #272724 !important;
        border: 0.5px solid rgba(232,230,225,0.08) !important;
        border-radius: 10px !important;
        color: #E8E6E1 !important;
    }

    /* ── Tabs ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 0.5px solid rgba(232,230,225,0.08) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #7A7873 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important;
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #E8E6E1 !important;
        border-bottom-color: #E24B4A !important;
    }

    /* ── Checkbox / toggle ───────────────────────────────── */
    .stCheckbox label {
        color: #E8E6E1 !important;
        font-size: 13px !important;
    }

    /* ── Séparateur ──────────────────────────────────────── */
    hr {
        border-color: rgba(232,230,225,0.08) !important;
        margin: 1rem 0 !important;
    }

    /* ── Territoire tag (liste) ──────────────────────────── */
    .terr-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #272724;
        border: 0.5px solid rgba(232,230,225,0.08);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: #E8E6E1;
        margin: 4px 4px 4px 0;
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .terr-tag:hover { border-color: rgba(232,230,225,0.2); }
    .terr-tag.active { border-color: #E24B4A; }

    /* ── Step indicator ──────────────────────────────────── */
    .step-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 0.5px solid rgba(232,230,225,0.06);
    }
    .step-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .step-dot.done    { background: #1D9E75; }
    .step-dot.running { background: #E24B4A; }
    .step-dot.pending { background: #4A4946; }
    .step-label {
        font-size: 13px;
        color: #E8E6E1;
        flex: 1;
    }
    .step-status {
        font-size: 11px;
        color: #7A7873;
    }

    /* ── Aléa risk row ───────────────────────────────────── */
    .risk-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 0.5px solid rgba(232,230,225,0.06);
        font-size: 13px;
    }
    .risk-name { color: #E8E6E1; }
    .risk-source { color: #4A4946; font-size: 11px; }

    </style>
    """, unsafe_allow_html=True)
