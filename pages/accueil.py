"""Page Accueil — MapOS"""
import streamlit as st
from components.style import C, topbar

def render():
    topbar()
    territoires = st.session_state.get("territoires", {})
    nb = len(territoires)

    st.markdown(f"""
    <div style="padding:3rem 0 2rem">
        <p class="mapos-eyebrow">Plateforme SIG · PICS / PCS</p>
        <h1 class="mapos-hero">Map<span style="color:{C['red']}">OS</span></h1>
        <p style="font-size:16px;color:{C['textMuted']};max-width:520px;line-height:1.7;margin-top:0.5rem">
            Génération automatisée des données cartographiques et des cartes d'aléas pour l'élaboration de PICS et PCS.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    total_communes = sum(len(t.get("communes",[])) for t in territoires.values())
    charges = sum(1 for t in territoires.values() if t.get("donnees_ok"))
    with col1: st.metric("Territoires", nb)
    with col2: st.metric("Communes", total_communes)
    with col3: st.metric("Données chargées", f"{charges}/{nb}")
    with col4: st.metric("Sources intégrées", "8")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<h2 class="mapos-section-title">Modules</h2>', unsafe_allow_html=True)

    modules = [
        ("📍","Territoire","territoire","Configurer les communes membres.","badge-neu","Étape 1"),
        ("⚠️","Aléas","aleas","Télécharger les données depuis Géorisques, SANDRE, IGN.","badge-info","Étape 2"),
        ("🗺️","Cartes","cartes","Générer les cartes thématiques par aléa.","badge-info","Étape 3"),
        ("📦","Export","export","Télécharger le GeoPackage QGIS et les PDF.","badge-info","Étape 4"),
    ]

    cols = st.columns(4)
    for i, (icon, nom, page, desc, badge_cls, etape) in enumerate(modules):
        with cols[i]:
            if st.button(f"{icon} {nom}", key=f"mod_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()
            st.markdown(f"""
            <div style="font-size:12px;color:{C['textMuted']};margin-top:6px;line-height:1.5">
                <span class="badge {badge_cls}">{etape}</span><br>
                <span style="margin-top:4px;display:block">{desc}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if territoires:
        st.markdown('<h2 class="mapos-section-title">Territoires configurés</h2>', unsafe_allow_html=True)
        for nom, config in territoires.items():
            dept = config.get("departement","—")
            nb_com = len(config.get("communes",[]))
            ok = config.get("donnees_ok", False)
            statut = '<span class="badge badge-ok">Données OK</span>' if ok else '<span class="badge badge-warn">En attente</span>'
            col_a, col_b = st.columns([6,1])
            with col_a:
                st.markdown(f"""
                <div class="mapos-card" style="margin-bottom:8px">
                    <div style="display:flex;align-items:center;justify-content:space-between">
                        <div>
                            <div class="mapos-card-title">{nom}</div>
                            <div class="mapos-small">Département {dept} · {nb_com} communes</div>
                        </div>
                        {statut}
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                if st.button("Ouvrir", key=f"open_{nom}"):
                    st.session_state.territoire_actif = nom
                    st.session_state.page = "aleas"
                    st.rerun()
    else:
        st.markdown(f"""
        <div class="mapos-card" style="text-align:center;padding:2.5rem">
            <div style="font-size:32px;margin-bottom:1rem">📍</div>
            <div class="mapos-card-title">Aucun territoire configuré</div>
            <div class="mapos-body" style="margin:0.5rem 0 1.5rem">Commencez par configurer votre premier territoire.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("＋  Configurer un territoire", type="primary"):
            st.session_state.page = "territoire"
            st.rerun()
