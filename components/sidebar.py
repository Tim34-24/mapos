"""
Sidebar MapOS — navigation + gestion multi-territoires.
"""

import streamlit as st
from components.style import C


NAV_ITEMS = [
    ("accueil",    "🏠", "Accueil"),
    ("territoire", "📍", "Territoire"),
    ("aleas",      "⚠️", "Aléas"),
    ("cartes",     "🗺️", "Cartes"),
    ("export",     "📦", "Export"),
]


def render_sidebar() -> str:
    """Affiche la sidebar et retourne la page active."""

    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:1.25rem 0.5rem 1rem;border-bottom:0.5px solid {C['border']};margin-bottom:1rem">
            <div style="font-size:22px;font-weight:500;letter-spacing:-0.02em;color:{C['text']}">
                Map<span style="color:{C['red']}">OS</span>
                <span style="width:7px;height:7px;border-radius:50%;background:{C['red']};
                      display:inline-block;margin-left:2px;vertical-align:middle"></span>
            </div>
            <div style="font-size:11px;color:{C['textFaint']};margin-top:3px;
                        text-transform:uppercase;letter-spacing:0.09em">
                par Sildaro
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sélecteur territoire
        _render_territoire_selector()

        st.markdown(f"""
        <div style="font-size:11px;font-weight:500;text-transform:uppercase;
                    letter-spacing:0.09em;color:{C['textFaint']};
                    padding:0.75rem 0.5rem 0.4rem">Navigation</div>
        """, unsafe_allow_html=True)

        # Navigation
        page_active = st.session_state.get("page", "accueil")
        for page_id, icon, label in NAV_ITEMS:
            is_active = page_id == page_active
            bg = f"rgba(226,75,74,0.12)" if is_active else "transparent"
            color = C["text"] if is_active else C["textMuted"]
            dot_bg = C["red"] if is_active else "transparent"

            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.page = page_id
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # Nouveau territoire
        if st.button("＋  Nouveau territoire", use_container_width=True):
            st.session_state.page = "territoire"
            st.session_state.territoire_actif = None
            st.rerun()

        # Version
        st.markdown(f"""
        <div style="position:absolute;bottom:1rem;left:1rem;right:1rem;
                    font-size:11px;color:{C['textFaint']};text-align:center">
            MapOS v0.1 · Données IGN / Géorisques
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("page", "accueil")


def _render_territoire_selector():
    """Affiche le sélecteur de territoire actif."""
    territoires = st.session_state.get("territoires", {})

    if not territoires:
        st.markdown(f"""
        <div style="background:{C['bgCard']};border:0.5px solid {C['border']};
                    border-radius:8px;padding:10px 12px;margin-bottom:1rem;
                    font-size:12px;color:{C['textMuted']}">
            Aucun territoire configuré
        </div>
        """, unsafe_allow_html=True)
        return

    noms = list(territoires.keys())
    actif = st.session_state.get("territoire_actif")
    idx = noms.index(actif) if actif in noms else 0

    choix = st.selectbox(
        "Territoire actif",
        noms,
        index=idx,
        key="select_territoire",
        label_visibility="collapsed",
    )

    if choix != actif:
        st.session_state.territoire_actif = choix
        st.session_state.donnees_chargees = {}
        st.rerun()

    st.markdown(f"""
    <div style="font-size:11px;color:{C['textFaint']};
                margin:-6px 0 1rem 4px">
        {len(territoires[choix].get('communes', []))} communes
    </div>
    """, unsafe_allow_html=True)
