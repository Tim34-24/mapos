"""
MapOS — Plateforme SIG pour l'élaboration de PICS / PCS
Développé par Sildaro
"""

import streamlit as st
from components.style import inject_global_css
from components.sidebar import render_sidebar
from pages import accueil, territoire, aleas, cartes, export

st.set_page_config(
    page_title="MapOS — Sildaro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

if "territoire_actif" not in st.session_state:
    st.session_state.territoire_actif = None
if "territoires" not in st.session_state:
    st.session_state.territoires = {}
if "page" not in st.session_state:
    st.session_state.page = "accueil"
if "donnees_chargees" not in st.session_state:
    st.session_state.donnees_chargees = {}

page = render_sidebar()

PAGES = {
    "accueil":    accueil.render,
    "territoire": territoire.render,
    "aleas":      aleas.render,
    "cartes":     cartes.render,
    "export":     export.render,
}

PAGES.get(page, accueil.render)()
