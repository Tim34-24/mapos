"""Page Aléas — téléchargement des données depuis Géorisques, SANDRE, IGN."""
import time
import requests
import geopandas as gpd
import streamlit as st
from shapely.ops import unary_union
from components.style import C, topbar

ALEAS = [
    {
        "id": "inondation_ppri",
        "nom": "Zones PPRI",
        "categorie": "Inondation",
        "source": "Géorisques",
        "badge": "badge-info",
        "description": "Plans de Prévention du Risque Inondation approuvés",
        "icon": "💧",
    },
    {
        "id": "inondation_azi",
        "nom": "Atlas zones inondables",
        "categorie": "Inondation",
        "source": "Géorisques",
        "badge": "badge-info",
        "description": "Atlas des zones inondables (AZI)",
        "icon": "💧",
    },
    {
        "id": "inondation_nappe",
        "nom": "Remontées de nappe",
        "categorie": "Inondation",
        "source": "Géorisques",
        "badge": "badge-info",
        "description": "Zones potentiellement sujettes aux remontées de nappe",
        "icon": "💧",
    },
    {
        "id": "catnat",
        "nom": "Arrêtés CATNAT",
        "categorie": "Historique",
        "source": "Géorisques",
        "badge": "badge-warn",
        "description": "Reconnaissance d'état de catastrophe naturelle",
        "icon": "📋",
    },
    {
        "id": "mvt_terrain",
        "nom": "Mouvements de terrain",
        "categorie": "Mouvements terrain",
        "source": "Géorisques",
        "badge": "badge-warn",
        "description": "Zonage PPRN mouvements de terrain",
        "icon": "⛰️",
    },
    {
        "id": "cavites",
        "nom": "Cavités souterraines",
        "categorie": "Mouvements terrain",
        "source": "Géorisques / BRGM",
        "badge": "badge-warn",
        "description": "Marnières, grottes, anciennes carrières",
        "icon": "🕳️",
    },
    {
        "id": "rga",
        "nom": "Retrait-gonflement argiles",
        "categorie": "Mouvements terrain",
        "source": "Géorisques / BRGM",
        "badge": "badge-warn",
        "description": "Aléa RGA — 3 niveaux (faible / moyen / fort)",
        "icon": "🪨",
    },
    {
        "id": "sismique",
        "nom": "Zonage sismique",
        "categorie": "Séisme",
        "source": "Géorisques",
        "badge": "badge-neu",
        "description": "Zones de sismicité réglementaires (1 à 5)",
        "icon": "〰️",
    },
    {
        "id": "radon",
        "nom": "Potentiel radon",
        "categorie": "Radon",
        "source": "Géorisques / IRSN",
        "badge": "badge-neu",
        "description": "Potentiel radon par commune (zones 1/2/3)",
        "icon": "☢️",
    },
    {
        "id": "icpe",
        "nom": "Sites ICPE",
        "categorie": "Risque industriel",
        "source": "Géorisques",
        "badge": "badge-alert",
        "description": "Installations classées pour la protection de l'environnement",
        "icon": "🏭",
    },
    {
        "id": "canalisations",
        "nom": "Canalisations TMD",
        "categorie": "TMD",
        "source": "Géorisques",
        "badge": "badge-alert",
        "description": "Canalisations de transport de matières dangereuses",
        "icon": "⚡",
    },
    {
        "id": "cours_eau",
        "nom": "Cours d'eau",
        "categorie": "Hydrologie",
        "source": "SANDRE / BD Carthage",
        "badge": "badge-info",
        "description": "Réseau hydrographique (rivières, ruisseaux, fossés)",
        "icon": "🌊",
    },
]


def render():
    actif = st.session_state.get("territoire_actif")
    topbar(actif)

    if not actif:
        st.warning("Aucun territoire actif. Configurez un territoire d'abord.")
        if st.button("Aller à Territoire"):
            st.session_state.page = "territoire"
            st.rerun()
        return

    config = st.session_state.territoires[actif]
    communes = config.get("communes", [])
    codes = [c["code"] for c in communes]

    st.markdown('<p class="mapos-eyebrow">Données sources</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="mapos-section-title">Aléas — {actif}</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mapos-body" style="margin-bottom:1.5rem">
        {len(communes)} communes · Département {config.get('departement','?')} ·
        Sources : Géorisques, SANDRE, IGN BD TOPO
    </div>
    """, unsafe_allow_html=True)

    donnees = st.session_state.donnees_chargees.get(actif, {})

    # Sélection des couches
    st.markdown(f'<div style="font-size:13px;color:{C["textMuted"]};margin-bottom:0.75rem">Sélectionner les couches à télécharger</div>', unsafe_allow_html=True)

    col_sel, col_btn = st.columns([4, 1])
    with col_sel:
        aleas_choisis = st.multiselect(
            "Couches",
            options=[a["id"] for a in ALEAS],
            default=[a["id"] for a in ALEAS],
            format_func=lambda x: next(f"{a['icon']} {a['nom']} ({a['source']})" for a in ALEAS if a["id"]==x),
            label_visibility="collapsed",
        )
    with col_btn:
        lancer = st.button("⬇  Télécharger", type="primary", use_container_width=True)

    # Tableau de statut
    _render_statut_table(donnees, aleas_choisis)

    # Lancement téléchargement
    if lancer:
        if not aleas_choisis:
            st.warning("Sélectionnez au moins une couche.")
        else:
            _telecharger_aleas(actif, codes, aleas_choisis, config)


def _render_statut_table(donnees: dict, aleas_choisis: list):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:13px;color:{C["textMuted"]};margin-bottom:0.75rem">Statut des couches</div>', unsafe_allow_html=True)

    categories = {}
    for a in ALEAS:
        cat = a["categorie"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)

    for cat, items in categories.items():
        st.markdown(f'<div style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:0.08em;color:{C["textFaint"]};margin:1rem 0 0.4rem">{cat}</div>', unsafe_allow_html=True)
        for a in items:
            est_selectionne = a["id"] in aleas_choisis
            est_charge = a["id"] in donnees
            nb_objets = donnees.get(a["id"], {}).get("nb", 0) if est_charge else None

            if est_charge:
                statut = f'<span class="badge badge-ok">✓ {nb_objets} objets</span>'
            elif est_selectionne:
                statut = f'<span class="badge badge-neu">Sélectionné</span>'
            else:
                statut = f'<span class="badge badge-neu" style="opacity:0.4">—</span>'

            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:7px 0;border-bottom:0.5px solid {C['border']}">
                <div style="display:flex;align-items:center;gap:10px">
                    <span style="font-size:16px">{a['icon']}</span>
                    <div>
                        <span style="font-size:13px;color:{C['text']}">{a['nom']}</span>
                        <span style="font-size:11px;color:{C['textFaint']};margin-left:8px">{a['source']}</span>
                    </div>
                </div>
                {statut}
            </div>
            """, unsafe_allow_html=True)


def _telecharger_aleas(actif: str, codes: list, aleas_choisis: list, config: dict):
    st.markdown("<hr>", unsafe_allow_html=True)
    progress_bar = st.progress(0, text="Initialisation...")
    log = st.empty()
    donnees = st.session_state.donnees_chargees.get(actif, {})

    total = len(aleas_choisis)

    for i, alea_id in enumerate(aleas_choisis):
        meta = next((a for a in ALEAS if a["id"] == alea_id), None)
        if not meta:
            continue

        log.markdown(f'<div class="mapos-small">⬇ {meta["nom"]}...</div>', unsafe_allow_html=True)
        progress_bar.progress((i) / total, text=f"Téléchargement : {meta['nom']}")

        try:
            result = _fetch_alea(alea_id, codes, config)
            donnees[alea_id] = result
            time.sleep(0.3)  # politesse API
        except Exception as e:
            donnees[alea_id] = {"nb": 0, "erreur": str(e), "data": None}

        progress_bar.progress((i + 1) / total, text=f"✓ {meta['nom']}")

    st.session_state.donnees_chargees[actif] = donnees
    st.session_state.territoires[actif]["donnees_ok"] = True
    progress_bar.progress(1.0, text="Téléchargement terminé ✓")
    log.empty()

    nb_ok  = sum(1 for v in donnees.values() if v.get("nb", 0) > 0)
    nb_err = sum(1 for v in donnees.values() if v.get("erreur"))
    st.success(f"✓ {nb_ok} couches chargées — {nb_err} erreur(s)")
    if nb_err:
        st.warning("Certaines couches n'ont pas pu être chargées (API indisponible ou territoire hors zone). Relancer pour réessayer.")
    st.rerun()


def _fetch_alea(alea_id: str, codes: list, config: dict) -> dict:
    """Fetch une couche d'aléa depuis l'API appropriée."""

    BASE_GR = "https://georisques.gouv.fr/api/v1"
    features = []

    # ── Géorisques : requêtes par commune ─────────────────────────
    if alea_id in ("inondation_ppri", "mvt_terrain"):
        type_ppr = "PPRNI" if alea_id == "inondation_ppri" else "PPRMT"
        for code in codes:
            try:
                r = requests.get(f"{BASE_GR}/gaspar/ppr",
                    params={"code_insee": code, "type_ppr": type_ppr, "page": 1, "page_size": 100},
                    timeout=15)
                if r.ok:
                    features.extend(r.json().get("data", []))
            except Exception:
                pass
        return {"nb": len(features), "data": features, "type": "json"}

    elif alea_id == "catnat":
        for code in codes:
            try:
                r = requests.get(f"{BASE_GR}/gaspar/catnat",
                    params={"code_insee": code, "page": 1, "page_size": 200},
                    timeout=15)
                if r.ok:
                    features.extend(r.json().get("data", []))
            except Exception:
                pass
        return {"nb": len(features), "data": features, "type": "json"}

    elif alea_id == "icpe":
        for code in codes:
            try:
                r = requests.get(f"{BASE_GR}/installations/search",
                    params={"code_insee": code, "page": 1, "page_size": 500},
                    timeout=15)
                if r.ok:
                    features.extend(r.json().get("data", []))
            except Exception:
                pass
        return {"nb": len(features), "data": features, "type": "json"}

    elif alea_id == "radon":
        resultats = {}
        for code in codes:
            try:
                r = requests.get(f"{BASE_GR}/radon",
                    params={"code_insee": code}, timeout=15)
                if r.ok:
                    data = r.json()
                    if isinstance(data, list) and data:
                        resultats[code] = data[0].get("potentiel_radon", "—")
                    elif isinstance(data, dict):
                        resultats[code] = data.get("potentiel_radon", "—")
            except Exception:
                pass
        return {"nb": len(resultats), "data": resultats, "type": "dict_commune"}

    elif alea_id == "sismique":
        resultats = {}
        for code in codes:
            try:
                r = requests.get(f"{BASE_GR}/zonages_sismiques",
                    params={"code_insee": code}, timeout=15)
                if r.ok:
                    data = r.json()
                    if isinstance(data, list) and data:
                        resultats[code] = data[0].get("zone_sismique", "—")
                    elif isinstance(data, dict):
                        resultats[code] = data.get("zone_sismique", "—")
            except Exception:
                pass
        return {"nb": len(resultats), "data": resultats, "type": "dict_commune"}

    # ── Géorisques WFS (couches géométriques) ─────────────────────
    elif alea_id in ("inondation_azi", "inondation_nappe", "cavites", "rga", "canalisations"):
        layer_map = {
            "inondation_azi":   "zonage_alea_inondation",
            "inondation_nappe": "remontees_nappes",
            "cavites":          "cavites_sol",
            "rga":              "alearg",
            "canalisations":    "canalisations_tmd",
        }
        # Calcul bbox depuis communes
        bbox = _bbox_communes(codes)
        if bbox:
            wfs_url = f"https://georisques.gouv.fr/services"
            try:
                r = requests.get(wfs_url, params={
                    "SERVICE": "WFS", "VERSION": "2.0.0",
                    "REQUEST": "GetFeature",
                    "TYPENAMES": layer_map.get(alea_id, ""),
                    "OUTPUTFORMAT": "application/json",
                    "BBOX": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]},EPSG:4326",
                    "COUNT": "2000",
                }, timeout=30)
                if r.ok and r.content:
                    gdf = gpd.read_file(r.content)
                    return {"nb": len(gdf), "data": gdf.to_json(), "type": "geojson"}
            except Exception as e:
                return {"nb": 0, "erreur": str(e), "data": None}
        return {"nb": 0, "data": None, "type": "geojson"}

    # ── SANDRE WFS — Cours d'eau ───────────────────────────────────
    elif alea_id == "cours_eau":
        bbox = _bbox_communes(codes)
        if bbox:
            xmin, ymin, xmax, ymax = bbox
            try:
                r = requests.get("https://services.sandre.eaufrance.fr/geo/hyd", params={
                    "SERVICE": "WFS", "VERSION": "2.0.0",
                    "REQUEST": "GetFeature", "TYPENAME": "CoursEau",
                    "OUTPUTFORMAT": "application/json", "SRSNAME": "EPSG:4326",
                    "BBOX": f"{ymin},{xmin},{ymax},{xmax},EPSG:4326",
                    "COUNT": "5000",
                }, timeout=30)
                if r.ok and r.content:
                    gdf = gpd.read_file(r.content)
                    return {"nb": len(gdf), "data": gdf.to_json(), "type": "geojson"}
            except Exception as e:
                return {"nb": 0, "erreur": str(e), "data": None}
        return {"nb": 0, "data": None}

    return {"nb": 0, "data": None, "erreur": "Source non implémentée"}


def _bbox_communes(codes: list) -> tuple | None:
    """Calcule la bbox WGS84 des communes via API Géo."""
    geometries = []
    for code in codes:
        try:
            r = requests.get(
                f"https://geo.api.gouv.fr/communes/{code}?fields=geometry&format=geojson&geometry=contour",
                timeout=10)
            if r.ok:
                geometries.append(r.json())
        except Exception:
            pass

    if not geometries:
        return None

    try:
        gdf = gpd.GeoDataFrame.from_features(geometries, crs="EPSG:4326")
        b = gdf.total_bounds  # xmin, ymin, xmax, ymax
        marge = 0.02
        return (b[0]-marge, b[1]-marge, b[2]+marge, b[3]+marge)
    except Exception:
        return None
