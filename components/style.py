"""
Injection du CSS global MapOS — identité visuelle dérivée de CrisisOS.
"""

import streamlit as st

# Tokens couleurs (reproduits depuis CrisisOS tokens.ts)
C = {
    "red":          "#E24B4A",
    "redDark":      "#C93D3C",
    "redBg":        "#2E1212",
    "redText":      "#F09595",
    "text":         "#E8E6E1",
    "textMuted":    "#7A7873",
    "textFaint":    "#4A4946",
    "bg":           "#1C1C1A",
    "bgCard":       "#272724",
    "bgSidebar":    "#202020",
    "border":       "rgba(232,230,225,0.08)",
    "borderHover":  "rgba(232,230,225,0.2)",
    "green":        "#1D9E75",
    "greenBg":      "#0D2B1E",
    "greenText":    "#5DCAA5",
    "amber":        "#BA7517",
    "amberBg":      "#2A1A05",
    "amberText":    "#EF9F27",
    "blueBg":       "#0C2A3E",
    "blueText":     "#85B7EB",
    "purple":       "#7F77DD",
    "purpleBg":     "#1E1B3A",
    "purpleText":   "#AFA9EC",
}


def inject_global_css():
    st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">

    <style>
    /* ── Reset & base ─────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C['bg']} !important;
        color: {C['text']};
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 14px;
        font-weight: 400;
    }}

    /* ── Sidebar ───────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background-color: {C['bgSidebar']} !important;
        border-right: 0.5px solid {C['border']};
    }}
    [data-testid="stSidebar"] * {{
        color: {C['text']} !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}

    /* ── Masquer éléments Streamlit natifs ─────────────────────── */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        display: none !important;
    }}

    /* ── Topbar custom ─────────────────────────────────────────── */
    .mapos-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        height: 52px;
        background: {C['bgCard']};
        border-bottom: 0.5px solid {C['border']};
        margin: -1rem -1rem 1.5rem -1rem;
    }}
    .mapos-logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 500;
        color: {C['text']};
        letter-spacing: -0.02em;
    }}
    .mapos-logo-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {C['red']};
        display: inline-block;
        margin-left: 2px;
        margin-bottom: 2px;
    }}
    .mapos-territoire-badge {{
        font-size: 12px;
        color: {C['textMuted']};
        background: {C['bg']};
        border: 0.5px solid {C['border']};
        border-radius: 8px;
        padding: 4px 12px;
    }}

    /* ── Cards ─────────────────────────────────────────────────── */
    .mapos-card {{
        background: {C['bgCard']};
        border: 0.5px solid {C['border']};
        border-radius: 12px;
        padding: 1.25rem;
        transition: border-color 0.15s, transform 0.15s;
        margin-bottom: 12px;
    }}
    .mapos-card:hover {{
        border-color: {C['borderHover']};
        transform: translateY(-2px);
    }}
    .mapos-card-large {{
        border-radius: 14px;
        padding: 1.5rem;
    }}

    /* ── Titres ─────────────────────────────────────────────────── */
    .mapos-hero {{
        font-size: 38px;
        font-weight: 500;
        color: {C['text']};
        letter-spacing: -0.025em;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }}
    .mapos-section-title {{
        font-size: 22px;
        font-weight: 500;
        color: {C['text']};
        letter-spacing: -0.02em;
        margin-bottom: 1rem;
    }}
    .mapos-card-title {{
        font-size: 16px;
        font-weight: 500;
        color: {C['text']};
        letter-spacing: -0.015em;
        margin-bottom: 0.25rem;
    }}
    .mapos-body {{
        font-size: 14px;
        color: {C['textMuted']};
        line-height: 1.6;
    }}
    .mapos-small {{
        font-size: 12px;
        color: {C['textMuted']};
    }}
    .mapos-eyebrow {{
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: {C['red']};
        margin-bottom: 0.5rem;
    }}

    /* ── Badges ─────────────────────────────────────────────────── */
    .badge {{
        display: inline-block;
        font-size: 10px;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
    }}
    .badge-ok    {{ background: {C['greenBg']}; color: {C['greenText']}; }}
    .badge-warn  {{ background: {C['amberBg']}; color: {C['amberText']}; }}
    .badge-alert {{ background: {C['redBg']};   color: {C['redText']};   }}
    .badge-info  {{ background: {C['blueBg']};  color: {C['blueText']};  }}
    .badge-ia    {{ background: {C['purpleBg']}; color: {C['purpleText']}; }}
    .badge-neu   {{ background: {C['bgCard']};  color: {C['textFaint']}; border: 0.5px solid {C['border']}; }}

    /* ── Boutons Streamlit ──────────────────────────────────────── */
    .stButton > button {{
        background: transparent;
        color: {C['text']};
        border: 0.5px solid {C['borderHover']};
        border-radius: 8px;
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 18px;
        transition: background 0.15s, border-color 0.15s;
    }}
    .stButton > button:hover {{
        background: {C['bgCard']};
        border-color: {C['borderHover']};
        color: {C['text']};
    }}
    .stButton > button[kind="primary"] {{
        background: {C['red']};
        border: none;
        color: #fff;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: {C['redDark']};
    }}

    /* ── Inputs ─────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background: {C['bg']} !important;
        color: {C['text']} !important;
        border: 0.5px solid {C['border']} !important;
        border-radius: 8px !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        font-size: 14px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: rgba(232,230,225,0.3) !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    .stSelectbox > div > div > div {{
        color: {C['text']} !important;
    }}

    /* ── Labels formulaire ──────────────────────────────────────── */
    label, .stSelectbox label, .stTextInput label,
    .stTextArea label, .stNumberInput label,
    .stCheckbox label, .stRadio label {{
        color: {C['textMuted']} !important;
        font-size: 13px !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}

    /* ── Checkbox / Radio ───────────────────────────────────────── */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] p,
    .stRadio > label > div[data-testid="stMarkdownContainer"] p {{
        color: {C['text']} !important;
        font-size: 14px !important;
    }}

    /* ── Progress bar ───────────────────────────────────────────── */
    .stProgress > div > div > div {{
        background: {C['red']} !important;
    }}
    .stProgress > div > div {{
        background: {C['bgCard']} !important;
        border-radius: 4px !important;
    }}

    /* ── Expander ───────────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background: {C['bgCard']} !important;
        color: {C['text']} !important;
        border: 0.5px solid {C['border']} !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}
    .streamlit-expanderContent {{
        background: {C['bgCard']} !important;
        border: 0.5px solid {C['border']} !important;
        border-top: none !important;
    }}

    /* ── Tabs ───────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 0.5px solid {C['border']};
        gap: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {C['textMuted']} !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        border: none !important;
        padding: 10px 20px !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {C['text']} !important;
        border-bottom: 2px solid {C['red']} !important;
        font-weight: 500 !important;
    }}

    /* ── Divider ─────────────────────────────────────────────────── */
    hr {{
        border: none;
        border-top: 0.5px solid {C['border']};
        margin: 1.5rem 0;
    }}

    /* ── Metric ─────────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: {C['bgCard']};
        border: 0.5px solid {C['border']};
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }}
    [data-testid="stMetricLabel"] {{
        color: {C['textMuted']} !important;
        font-size: 12px !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {C['text']} !important;
        font-size: 24px !important;
        font-weight: 500 !important;
    }}

    /* ── Alertes Streamlit ──────────────────────────────────────── */
    .stAlert {{
        border-radius: 8px !important;
        border: 0.5px solid {C['border']} !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}

    /* ── Grille de modules ──────────────────────────────────────── */
    .mapos-modules-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 10px;
        margin: 1rem 0;
    }}
    .mapos-module-card {{
        background: {C['bgCard']};
        border: 0.5px solid {C['border']};
        border-radius: 12px;
        padding: 1.25rem;
        cursor: pointer;
        transition: border-color 0.15s, transform 0.15s;
        text-decoration: none;
    }}
    .mapos-module-card:hover {{
        border-color: {C['borderHover']};
        transform: translateY(-2px);
    }}
    .mapos-module-icon {{
        font-size: 22px;
        margin-bottom: 0.75rem;
    }}

    /* ── Sidebar nav ─────────────────────────────────────────────── */
    .sidebar-nav-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        color: {C['textMuted']};
        font-size: 13px;
        font-weight: 400;
        transition: background 0.1s, color 0.1s;
        margin-bottom: 2px;
    }}
    .sidebar-nav-item:hover {{
        background: rgba(232,230,225,0.05);
        color: {C['text']};
    }}
    .sidebar-nav-item.active {{
        background: rgba(226,75,74,0.12);
        color: {C['text']};
    }}
    .sidebar-nav-item.active .nav-dot {{
        background: {C['red']};
    }}
    .nav-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: transparent;
        flex-shrink: 0;
    }}

    /* ── Scrollbar ──────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: {C['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {C['textFaint']}; border-radius: 2px; }}

    /* ── Contenu principal ──────────────────────────────────────── */
    .main .block-container {{
        padding: 1rem 2rem 2rem 2rem !important;
        max-width: 1200px;
    }}
    </style>
    """, unsafe_allow_html=True)


def card(contenu_html: str, large: bool = False) -> str:
    cls = "mapos-card mapos-card-large" if large else "mapos-card"
    return f'<div class="{cls}">{contenu_html}</div>'


def badge(texte: str, type: str = "neu") -> str:
    return f'<span class="badge badge-{type}">{texte}</span>'


def eyebrow(texte: str) -> str:
    return f'<p class="mapos-eyebrow">{texte}</p>'


def section_title(texte: str) -> str:
    return f'<h2 class="mapos-section-title">{texte}</h2>'


def topbar(territoire: str = None):
    terr_html = ""
    if territoire:
        terr_html = f'<span class="mapos-territoire-badge">📍 {territoire}</span>'
    st.markdown(f"""
    <div class="mapos-topbar">
        <div class="mapos-logo">
            Map<span style="color:{C['red']}">OS</span><span class="mapos-logo-dot"></span>
        </div>
        {terr_html}
        <span class="mapos-small" style="color:{C['textFaint']}"></span>
    </div>
    """, unsafe_allow_html=True)
