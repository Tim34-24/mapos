"""Page Accueil — MapOS"""
import streamlit as st
from components.style import C, FONT, badge_html, card_html, eyebrow_html, section_title_html, topbar

def render():
    topbar()
    territoires = st.session_state.get("territoires", {})
    nb = len(territoires)

    # Hero
    st.markdown(f"""
    <div style="padding:3rem 0 2rem">
        {eyebrow_html("Plateforme SIG · PICS / PCS")}
        <h1 style="font-size:38px;font-weight:500;color:{C['text']};
                   letter-spacing:-0.025em;line-height:1.15;font-family:{FONT}">
            Map<span style="color:{C['red']}">OS</span>
        </h1>
        <p style="font-size:16px;color:{C['textMuted']};max-width:520px;
                  line-height:1.7;margin-top:0.5rem;font-family:{FONT}">
            Génération automatisée des données cartographiques
            et des cartes d'aléas pour l'élaboration de PICS et PCS.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Métriques
    total_communes = sum(len(t.get("communes", [])) for t in territoires.values())
    charges = sum(1 for t in territoires.values() if t.get("donnees_ok"))
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Territoires", nb)
    with col2: st.metric("Communes", total_communes)
    with col3: st.metric("Données chargées", f"{charges}/{nb}")
    with col4: st.metric("Sources intégrées", "8")

    st.markdown("<hr style='border:none;border-top:0.5px solid rgba(232,230,225,0.08);margin:1.5rem 0'>",
                unsafe_allow_html=True)

    # Modules
    st.markdown(section_title_html("Modules"), unsafe_allow_html=True)

    modules = [
        ("📍", "Territoire",  "territoire", "Configurer les communes membres.",       "neu",  "Étape 1"),
        ("⚠️", "Aléas",       "aleas",      "Télécharger depuis Géorisques, SANDRE, IGN.", "info", "Étape 2"),
        ("🗺️", "Cartes",       "cartes",     "Générer les cartes thématiques par aléa.", "info", "Étape 3"),
        ("📦", "Export",       "export",     "Télécharger le GeoPackage QGIS et les PDF.", "info", "Étape 4"),
    ]

    cols = st.columns(4)
    for i, (icon, nom, page, desc, badge_type, etape) in enumerate(modules):
        with cols[i]:
            if st.button(f"{icon} {nom}", key=f"mod_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()
            st.markdown(f"""
            <div style="font-size:12px;color:{C['textMuted']};margin-top:6px;
                        line-height:1.5;font-family:{FONT}">
                {badge_html(etape, badge_type)}
                <span style="margin-top:4px;display:block">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:0.5px solid rgba(232,230,225,0.08);margin:1.5rem 0'>",
                unsafe_allow_html=True)

    # Territoires
    if territoires:
        st.markdown(section_title_html("Territoires configurés"), unsafe_allow_html=True)
        for nom, config in territoires.items():
            dept   = config.get("departement", "—")
            nb_com = len(config.get("communes", []))
            ok     = config.get("donnees_ok", False)
            statut = badge_html("Données OK", "ok") if ok else badge_html("En attente", "warn")
            col_a, col_b = st.columns([6, 1])
            with col_a:
                st.markdown(f"""
                <div style="background:{C['bgCard']};border:0.5px solid {C['border']};
                            border-radius:12px;padding:1rem 1.25rem;margin-bottom:8px">
                    <div style="display:flex;align-items:center;justify-content:space-between">
                        <div>
                            <div style="font-size:16px;font-weight:500;color:{C['text']};
                                        font-family:{FONT}">{nom}</div>
                            <div style="font-size:12px;color:{C['textMuted']};font-family:{FONT}">
                                Département {dept} · {nb_com} communes
                            </div>
                        </div>
                        {statut}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if st.button("Ouvrir", key=f"open_{nom}"):
                    st.session_state.territoire_actif = nom
                    st.session_state.page = "aleas"
                    st.rerun()
    else:
        st.markdown(f"""
        <div style="background:{C['bgCard']};border:0.5px solid {C['border']};
                    border-radius:12px;padding:2.5rem;text-align:center">
            <div style="font-size:32px;margin-bottom:1rem">📍</div>
            <div style="font-size:16px;font-weight:500;color:{C['text']};font-family:{FONT}">
                Aucun territoire configuré
            </div>
            <div style="font-size:14px;color:{C['textMuted']};margin:0.5rem 0 1.5rem;font-family:{FONT}">
                Commencez par configurer votre premier territoire.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("＋  Configurer un territoire", type="primary"):
            st.session_state.page = "territoire"
            st.rerun()
