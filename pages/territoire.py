"""Page Territoire — configuration et gestion multi-territoires."""
import streamlit as st
import requests
from components.style import C, topbar

COMMUNES_GALLY = [
    {"code":"78016","nom":"Andelu"},{"code":"78047","nom":"Bazemont"},
    {"code":"78139","nom":"Chavenay"},{"code":"78178","nom":"Crespières"},
    {"code":"78196","nom":"Davron"},{"code":"78234","nom":"Feucherolles"},
    {"code":"78299","nom":"Herbeville"},{"code":"78368","nom":"Mareil-sur-Mauldre"},
    {"code":"78382","nom":"Maule"},{"code":"78419","nom":"Montainville"},
    {"code":"78570","nom":"Saint-Nom-la-Bretèche"},
]

def render():
    topbar(st.session_state.get("territoire_actif"))
    st.markdown('<p class="mapos-eyebrow">Configuration</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="mapos-section-title">Territoire</h2>', unsafe_allow_html=True)

    tab_nouveau, tab_liste = st.tabs(["Nouveau territoire", "Territoires existants"])

    with tab_nouveau:
        _form_nouveau_territoire()

    with tab_liste:
        _liste_territoires()


def _form_nouveau_territoire():
    st.markdown(f'<div class="mapos-body" style="margin-bottom:1.5rem">Renseignez les informations du territoire pour lequel vous souhaitez générer des données SIG.</div>', unsafe_allow_html=True)

    with st.form("form_territoire"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de l'intercommunalité *", placeholder="ex: Gally Mauldre")
        with col2:
            dept = st.text_input("Numéro de département *", placeholder="ex: 78", max_chars=3)

        col3, col4 = st.columns(2)
        with col3:
            code_epci = st.text_input("Code EPCI (optionnel)", placeholder="ex: 200034130")
        with col4:
            buffer_km = st.number_input("Buffer autour du territoire (km)", min_value=0, max_value=10, value=2)

        st.markdown(f'<div style="margin:1rem 0 0.5rem"><span style="font-size:13px;color:{C["textMuted"]}">Communes membres *</span></div>', unsafe_allow_html=True)

        methode = st.radio(
            "Méthode de saisie",
            ["Saisie manuelle", "Charger exemple Gally Mauldre"],
            horizontal=True,
            label_visibility="collapsed",
        )

        communes_saisies = []
        if methode == "Charger exemple Gally Mauldre":
            st.markdown(f"""
            <div style="background:{C['bgCard']};border:0.5px solid {C['border']};
                        border-radius:8px;padding:12px;margin:0.5rem 0">
                <div style="font-size:12px;color:{C['textMuted']};margin-bottom:8px">
                    11 communes pré-chargées
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:6px">
                    {''.join(f'<span class="badge badge-neu">{c["code"]} {c["nom"]}</span>' for c in COMMUNES_GALLY)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            communes_saisies = COMMUNES_GALLY
        else:
            texte = st.text_area(
                "Codes INSEE (un par ligne, format: CODE NOM)",
                placeholder="78016 Andelu\n78047 Bazemont\n78139 Chavenay",
                height=180,
            )
            if texte.strip():
                for ligne in texte.strip().splitlines():
                    parts = ligne.strip().split(None, 1)
                    if len(parts) == 2:
                        communes_saisies.append({"code": parts[0].strip(), "nom": parts[1].strip()})
                    elif len(parts) == 1 and len(parts[0]) == 5:
                        communes_saisies.append({"code": parts[0].strip(), "nom": ""})

        submitted = st.form_submit_button("Enregistrer le territoire", type="primary", use_container_width=True)

        if submitted:
            erreurs = []
            if not nom.strip(): erreurs.append("Le nom est obligatoire.")
            if not dept.strip(): erreurs.append("Le département est obligatoire.")
            if not communes_saisies: erreurs.append("Au moins une commune est requise.")

            if erreurs:
                for e in erreurs:
                    st.error(e)
            else:
                config = {
                    "nom": nom.strip(),
                    "departement": dept.strip().zfill(2),
                    "code_epci": code_epci.strip(),
                    "buffer_km": buffer_km,
                    "communes": communes_saisies if communes_saisies else COMMUNES_GALLY,
                    "donnees_ok": False,
                }
                if "territoires" not in st.session_state:
                    st.session_state.territoires = {}
                st.session_state.territoires[nom.strip()] = config
                st.session_state.territoire_actif = nom.strip()
                st.success(f"✓ Territoire « {nom} » configuré avec {len(communes_saisies)} communes.")
                st.info("Passez à l'étape **Aléas** pour télécharger les données.")


def _liste_territoires():
    territoires = st.session_state.get("territoires", {})
    if not territoires:
        st.markdown(f'<div class="mapos-body">Aucun territoire configuré.</div>', unsafe_allow_html=True)
        return

    for nom, config in list(territoires.items()):
        with st.expander(f"📍 {nom} — D{config.get('departement','?')} · {len(config.get('communes',[]))} communes"):
            col_a, col_b, col_c = st.columns([3,2,1])
            with col_a:
                st.markdown(f"""
                <div class="mapos-small">
                    <b style="color:{C['text']}">EPCI</b> {config.get('code_epci','—')}<br>
                    <b style="color:{C['text']}">Buffer</b> {config.get('buffer_km',2)} km<br>
                    <b style="color:{C['text']}">Données</b> {'✓ chargées' if config.get('donnees_ok') else 'en attente'}
                </div>""", unsafe_allow_html=True)
            with col_b:
                communes = config.get("communes", [])
                st.markdown(f"""
                <div style="display:flex;flex-wrap:wrap;gap:4px">
                    {''.join(f'<span class="badge badge-neu">{c["code"]}</span>' for c in communes[:8])}
                    {f'<span class="badge badge-neu">+{len(communes)-8}</span>' if len(communes)>8 else ''}
                </div>""", unsafe_allow_html=True)
            with col_c:
                if st.button("Activer", key=f"activer_{nom}"):
                    st.session_state.territoire_actif = nom
                    st.rerun()
                if st.button("Supprimer", key=f"suppr_{nom}"):
                    del st.session_state.territoires[nom]
                    if st.session_state.territoire_actif == nom:
                        st.session_state.territoire_actif = None
                    st.rerun()
