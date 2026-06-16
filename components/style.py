"""
Tokens et composants visuels MapOS.
Tout en styles inline — pas de classes CSS externes (plus fiable sur Streamlit Cloud).
"""

import streamlit as st

C = {
    "red":         "#E24B4A",
    "redDark":     "#C93D3C",
    "redBg":       "#2E1212",
    "redText":     "#F09595",
    "text":        "#E8E6E1",
    "textMuted":   "#7A7873",
    "textFaint":   "#4A4946",
    "bg":          "#1C1C1A",
    "bgCard":      "#272724",
    "bgSidebar":   "#202020",
    "border":      "rgba(232,230,225,0.08)",
    "borderHover": "rgba(232,230,225,0.2)",
    "green":       "#1D9E75",
    "greenBg":     "#0D2B1E",
    "greenText":   "#5DCAA5",
    "amber":       "#BA7517",
    "amberBg":     "#2A1A05",
    "amberText":   "#EF9F27",
    "blueBg":      "#0C2A3E",
    "blueText":    "#85B7EB",
    "purple":      "#7F77DD",
    "purpleBg":    "#1E1B3A",
    "purpleText":  "#AFA9EC",
}

# Badges inline — tuples (fond, texte)
BADGE = {
    "ok":    (C["greenBg"],  C["greenText"]),
    "warn":  (C["amberBg"],  C["amberText"]),
    "alert": (C["redBg"],    C["redText"]),
    "info":  (C["blueBg"],   C["blueText"]),
    "ia":    (C["purpleBg"], C["purpleText"]),
    "neu":   (C["bgCard"],   C["textFaint"]),
}

FONT = "'Inter', system-ui, sans-serif"


def inject_global_css():
    """CSS minimal — uniquement ce que Streamlit accepte de façon fiable."""
    st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C['bg']} !important;
        color: {C['text']};
        font-family: {FONT};
    }}
    [data-testid="stSidebar"] {{
        background-color: {C['bgSidebar']} !important;
        border-right: 0.5px solid {C['border']};
    }}
    [data-testid="stSidebar"] * {{ color: {C['text']} !important; font-family: {FONT} !important; }}
    #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display:none !important; }}
    .stButton > button {{
        background: transparent; color: {C['text']};
        border: 0.5px solid {C['borderHover']}; border-radius: 8px;
        font-family: {FONT}; font-size: 13px; font-weight: 500; padding: 8px 18px;
    }}
    .stButton > button:hover {{ background: {C['bgCard']}; }}
    .stButton > button[kind="primary"] {{ background: {C['red']}; border: none; color: #fff; }}
    .stButton > button[kind="primary"]:hover {{ background: {C['redDark']}; }}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {{
        background: {C['bg']} !important; color: {C['text']} !important;
        border: 0.5px solid {C['border']} !important; border-radius: 8px !important;
        font-family: {FONT} !important; font-size: 14px !important;
    }}
    label {{ color: {C['textMuted']} !important; font-size: 13px !important; font-family: {FONT} !important; }}
    [data-testid="stMetric"] {{
        background: {C['bgCard']}; border: 0.5px solid {C['border']};
        border-radius: 12px; padding: 1rem 1.25rem;
    }}
    [data-testid="stMetricLabel"] {{ color: {C['textMuted']} !important; font-size: 12px !important; }}
    [data-testid="stMetricValue"] {{ color: {C['text']} !important; font-size: 24px !important; font-weight: 500 !important; }}
    .stTabs [data-baseweb="tab-list"] {{ background: transparent !important; border-bottom: 0.5px solid {C['border']}; }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important; color: {C['textMuted']} !important;
        font-family: {FONT} !important; font-size: 14px !important; border: none !important; padding: 10px 20px !important;
    }}
    .stTabs [aria-selected="true"] {{ color: {C['text']} !important; border-bottom: 2px solid {C['red']} !important; font-weight: 500 !important; }}
    hr {{ border: none; border-top: 0.5px solid {C['border']}; margin: 1.5rem 0; }}
    .stProgress > div > div > div {{ background: {C['red']} !important; }}
    .streamlit-expanderHeader {{
        background: {C['bgCard']} !important; color: {C['text']} !important;
        border: 0.5px solid {C['border']} !important; border-radius: 8px !important;
    }}
    .main .block-container {{ padding: 1rem 2rem 2rem 2rem !important; max-width: 1200px; }}
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: {C['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {C['textFaint']}; border-radius: 2px; }}
    </style>
    """, unsafe_allow_html=True)


# ── Helpers inline ────────────────────────────────────────────────

def badge_html(texte: str, type: str = "neu") -> str:
    bg, fg = BADGE.get(type, BADGE["neu"])
    return (f'<span style="display:inline-block;font-size:10px;font-weight:500;'
            f'padding:2px 8px;border-radius:10px;font-family:{FONT};'
            f'background:{bg};color:{fg}">{texte}</span>')


def card_html(contenu: str, extra_style: str = "") -> str:
    return (f'<div style="background:{C["bgCard"]};border:0.5px solid {C["border"]};'
            f'border-radius:12px;padding:1.25rem;margin-bottom:12px;{extra_style}">'
            f'{contenu}</div>')


def eyebrow_html(texte: str) -> str:
    return (f'<p style="font-size:11px;font-weight:500;text-transform:uppercase;'
            f'letter-spacing:0.09em;color:{C["red"]};font-family:{FONT};margin-bottom:0.5rem">'
            f'{texte}</p>')


def section_title_html(texte: str) -> str:
    return (f'<h2 style="font-size:22px;font-weight:500;color:{C["text"]};'
            f'letter-spacing:-0.02em;font-family:{FONT};margin-bottom:1rem">'
            f'{texte}</h2>')


def small_html(texte: str) -> str:
    return f'<span style="font-size:12px;color:{C["textMuted"]};font-family:{FONT}">{texte}</span>'


def topbar(territoire: str = None):
    terr_html = ""
    if territoire:
        terr_html = (f'<span style="font-size:12px;color:{C["textMuted"]};'
                     f'background:{C["bg"]};border:0.5px solid {C["border"]};'
                     f'border-radius:8px;padding:4px 12px;font-family:{FONT}">📍 {territoire}</span>')

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:0 2rem;height:52px;background:{C['bgCard']};
                border-bottom:0.5px solid {C['border']};
                margin:-1rem -1rem 1.5rem -1rem">
        <div style="display:flex;align-items:center;gap:6px;font-size:18px;
                    font-weight:500;letter-spacing:-0.02em;color:{C['text']};
                    font-family:{FONT}">
            Map<span style="color:{C['red']}">OS</span>
            <span style="width:7px;height:7px;border-radius:50%;
                         background:{C['red']};display:inline-block"></span>
        </div>
        {terr_html}
    </div>
    """, unsafe_allow_html=True)
