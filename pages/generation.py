"""
Page Génération — Sélection des couches et lancement
"""

import streamlit as st
import threading
from core.state import get_territoire_actif, charger_territoires
from core.territoire import ALEAS_CONFIG, generer_geopackage


def render():
    territoire = get_territoire_actif()

    # ── Sélecteur de territoire ──────────────────────────────
    territoires = charger_territoires()
    if not territoires:
        st.markdown("""
        <div class="mapos-card" style="text-align:center; padding: 2.5rem;">
            <div style="font-size: 14px; color: #7A7873;">
                Aucun territoire configuré. Allez dans <b>Territoires</b> pour en créer un.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="card-eyebrow">GÉNÉRATION</div>
        <div class="page-title">Données SIG</div>
        <div class="page-subtitle">
            Sélectionnez un territoire, choisissez les couches à télécharger
            et lancez la génération du GeoPackage.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sélecteur territoire
    noms = {t["id"]: t["nom"] for t in territoires}
    actif_id = st.session_state.get("territoire_actif", territoires[0]["id"])
    choix = st.selectbox(
        "Territoire",
        options=list(noms.keys()),
        format_func=lambda x: noms[x],
        index=list(noms.keys()).index(actif_id) if actif_id in noms else 0,
        key="select_territoire"
    )
    if choix != st.session_state.get("territoire_actif"):
        st.session_state.territoire_actif = choix
        st.rerun()

    territoire = get_territoire_actif()
    if not territoire:
        return

    codes   = [c["code"] for c in territoire["communes"]]
    dept    = territoire["departement"]
    nb_comm = len(codes)

    # ── Infos territoire ─────────────────────────────────────
    st.markdown(f"""
    <div class="mapos-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div>
                <div class="metric-label">Territoire</div>
                <div style="font-size: 15px; font-weight: 500; color: #E8E6E1;">
                    {territoire['nom']}
                </div>
            </div>
            <div>
                <div class="metric-label">Département</div>
                <div style="font-size: 15px; font-weight: 500; color: #E8E6E1;">D{dept}</div>
            </div>
            <div>
                <div class="metric-label">Communes</div>
                <div style="font-size: 15px; font-weight: 500; color: #E8E6E1;">{nb_comm}</div>
            </div>
            <div>
                <div class="metric-label">Code EPCI</div>
                <div style="font-size: 15px; font-weight: 500; color: #E8E6E1;">
                    {territoire.get('code_epci', '—')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 3])

    # ── Sélection couches ────────────────────────────────────
    with col_left:
        st.markdown('<div class="section-title">Couches de base</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="mapos-card-lg">""", unsafe_allow_html=True)

        couches = {
            "limites":    st.checkbox("Limites administratives", value=True, key="c_limites"),
            "hydrologie": st.checkbox("Hydrologie (cours d'eau, plans d'eau)", value=True, key="c_hydro"),
            "routes":     st.checkbox("Routes et voies ferrées", value=True, key="c_routes"),
            "batiments":  st.checkbox("Bâtiments", value=True, key="c_batiments"),
            "vegetation": st.checkbox("Végétation / occupation du sol", value=True, key="c_veget"),
        }
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:1rem;">Couches d\'aléas (Géorisques)</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div class="mapos-card-lg">""", unsafe_allow_html=True)

        aleas_selectionnes = []
        for key, config in ALEAS_CONFIG.items():
            checked = st.checkbox(
                f"{config['icone']} {config['nom']}",
                value=True,
                key=f"alea_{key}"
            )
            if checked:
                aleas_selectionnes.append(key)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Log et lancement ─────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-title">Journal de génération</div>', unsafe_allow_html=True)

        log_placeholder = st.empty()
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        def render_log(messages: list):
            if not messages:
                log_placeholder.markdown("""
                <div class="mapos-card-lg" style="height: 420px; display: flex;
                     align-items: center; justify-content: center;">
                    <div style="text-align: center; color: #4A4946; font-size: 13px;">
                        Le journal apparaîtra ici pendant la génération.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return

            lignes_html = ""
            for msg in messages[-25:]:  # 25 dernières lignes
                if msg.startswith("✅") or msg.startswith("✓"):
                    color = "#5DCAA5"
                elif msg.startswith("❌") or msg.startswith("✗"):
                    color = "#F09595"
                elif msg.startswith("⚠"):
                    color = "#EF9F27"
                else:
                    color = "#7A7873"

                lignes_html += f'<div style="color: {color}; font-size: 12px; line-height: 1.8;">{msg}</div>'

            log_placeholder.markdown(f"""
            <div class="mapos-card-lg" style="height: 420px; overflow-y: auto;
                 font-family: monospace;">
                {lignes_html}
            </div>
            """, unsafe_allow_html=True)

        render_log(st.session_state.get("generation_log", []))

        # Bouton de lancement
        st.markdown('<div style="height: 0.75rem"></div>', unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            lancer = st.button(
                "▶  Lancer la génération",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.get("generation_en_cours", False)
            )
        with col_btn2:
            if st.button("🗑  Réinitialiser le journal", use_container_width=True):
                st.session_state.generation_log = []
                st.rerun()

        # ── Génération synchrone (Streamlit Cloud compatible) ─
        if lancer:
            st.session_state.generation_log = []
            st.session_state.generation_en_cours = True

            log_msgs = []

            def log_cb(msg):
                log_msgs.append(msg)
                st.session_state.generation_log = log_msgs.copy()

            progress_bar = progress_placeholder.progress(0, text="Initialisation...")

            def progress_cb(current, total, msg=""):
                if total > 0:
                    pct = min(int(current / total * 100), 100)
                    progress_bar.progress(pct, text=msg[:80])

            with st.spinner("Génération en cours..."):
                try:
                    gpkg = generer_geopackage(
                        territoire=territoire,
                        couches_voulues=couches,
                        aleas_voulus=aleas_selectionnes,
                        progress_cb=progress_cb,
                        log_cb=log_cb,
                    )

                    if gpkg:
                        progress_placeholder.progress(100, text="Terminé !")
                        status_placeholder.success(
                            f"✅ GeoPackage généré avec succès : {gpkg.name}"
                        )
                        st.session_state.gpkg_path = str(gpkg)
                    else:
                        status_placeholder.error("❌ La génération a échoué. Consultez le journal.")

                except Exception as e:
                    log_cb(f"❌ Erreur inattendue : {e}")
                    status_placeholder.error(f"Erreur : {e}")
                finally:
                    st.session_state.generation_en_cours = False

            # Mise à jour du log
            render_log(st.session_state.generation_log)

            # Bouton accéder aux exports
            if st.session_state.get("gpkg_path"):
                if st.button("📦  Voir les exports →", type="primary", use_container_width=True):
                    st.session_state.page = "exports"
                    st.rerun()
