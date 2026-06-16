"""
Gestion des territoires — API Géo, Géorisques, BD TOPO
"""

import requests
import json
import time
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union

from core.state import charger_territoires, sauvegarder_territoire

# ── Cache BD TOPO ────────────────────────────────────────────
CACHE_DIR = Path(__file__).parent.parent / "_cache_bdtopo"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_INDEX = CACHE_DIR / "index.json"

# ── Dossier data ─────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# =============================================================================
# API Géo — récupération communes
# =============================================================================

def rechercher_communes_api(query: str) -> list:
    """Recherche des communes par nom via API Géo."""
    try:
        r = requests.get(
            "https://geo.api.gouv.fr/communes",
            params={"nom": query, "fields": "nom,code,codeDepartement,population", "limit": 15},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def recuperer_commune(code_insee: str) -> dict | None:
    """Récupère les infos + géométrie d'une commune."""
    try:
        r = requests.get(
            f"https://geo.api.gouv.fr/communes/{code_insee}",
            params={"fields": "nom,code,codeDepartement,population,geometry", "format": "geojson", "geometry": "contour"},
            timeout=15
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def recuperer_geometries_communes(codes_insee: list, progress_cb=None) -> gpd.GeoDataFrame | None:
    """Récupère les géométries de toutes les communes membres."""
    features = []
    for i, code in enumerate(codes_insee):
        data = recuperer_commune(code)
        if data:
            features.append(data)
        if progress_cb:
            progress_cb(i + 1, len(codes_insee), f"Commune {code}...")
        time.sleep(0.05)

    if not features:
        return None

    gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
    return gdf.to_crs("EPSG:2154")


# =============================================================================
# Géorisques — couches d'aléas
# =============================================================================

GEORISQUES_BASE = "https://georisques.gouv.fr/api/v1"

ALEAS_CONFIG = {
    "ppri": {
        "nom": "Zones PPRI",
        "endpoint": "/gaspar/ppr",
        "params_extra": {"type_ppr": "PPRNI"},
        "type": "polygon",
        "couleur": "#1a6eb5",
        "icone": "💧",
    },
    "pprn_mouvements": {
        "nom": "PPRN Mouvements de terrain",
        "endpoint": "/gaspar/ppr",
        "params_extra": {"type_ppr": "PPRMT"},
        "type": "polygon",
        "couleur": "#8B4513",
        "icone": "⛰️",
    },
    "pprn_rga": {
        "nom": "PPRN Retrait-gonflement argiles",
        "endpoint": "/gaspar/ppr",
        "params_extra": {"type_ppr": "PPRRGA"},
        "type": "polygon",
        "couleur": "#DAA520",
        "icone": "🟡",
    },
    "catnat": {
        "nom": "Catastrophes naturelles",
        "endpoint": "/gaspar/catnat",
        "params_extra": {},
        "type": "point",
        "couleur": "#E24B4A",
        "icone": "⚠️",
    },
    "cavites": {
        "nom": "Cavités souterraines",
        "endpoint": "/cavites",
        "params_extra": {},
        "type": "point",
        "couleur": "#6B3A2A",
        "icone": "🕳️",
    },
    "icpe": {
        "nom": "Installations classées (ICPE)",
        "endpoint": "/installations/search",
        "params_extra": {},
        "type": "point",
        "couleur": "#FF6B35",
        "icone": "🏭",
    },
    "argiles": {
        "nom": "Aléa retrait-gonflement argiles",
        "endpoint": "/argiles",
        "params_extra": {},
        "type": "polygon",
        "couleur": "#C9A84C",
        "icone": "🟤",
    },
    "radon": {
        "nom": "Potentiel radon",
        "endpoint": "/radon",
        "params_extra": {},
        "type": "commune",
        "couleur": "#9B59B6",
        "icone": "☢️",
    },
    "canalisations": {
        "nom": "Canalisations TMD",
        "endpoint": "/canalisations",
        "params_extra": {},
        "type": "line",
        "couleur": "#E67E22",
        "icone": "🔧",
    },
    "sismicite": {
        "nom": "Zonage sismique",
        "endpoint": "/seisme/commune",
        "params_extra": {},
        "type": "commune",
        "couleur": "#85B7EB",
        "icone": "〰️",
    },
}


def fetch_georisques(endpoint: str, code_insee: str, params_extra: dict = {}) -> list:
    """Appel API Géorisques pour une commune."""
    try:
        params = {"code_insee": code_insee, "page": 1, "page_size": 100, **params_extra}
        r = requests.get(
            f"{GEORISQUES_BASE}{endpoint}",
            params=params,
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        # Différentes structures selon les endpoints
        if isinstance(data, list):
            return data
        if "data" in data:
            return data["data"]
        if "features" in data:
            return data["features"]
        return [data] if data else []
    except Exception:
        return []


def recuperer_aleas_territoire(codes_insee: list, aleas_voulus: list, progress_cb=None) -> dict:
    """
    Récupère toutes les couches d'aléas Géorisques pour les communes membres.
    Retourne un dict {nom_alea: liste_features}.
    """
    resultats = {}
    total = len(aleas_voulus) * len(codes_insee)
    step = 0

    for alea_key in aleas_voulus:
        config = ALEAS_CONFIG.get(alea_key)
        if not config:
            continue

        features_alea = []
        for code in codes_insee:
            features = fetch_georisques(
                config["endpoint"], code, config.get("params_extra", {})
            )
            for f in features:
                f["_commune"] = code
                f["_alea"] = alea_key
            features_alea.extend(features)
            step += 1
            if progress_cb:
                progress_cb(step, total, f"{config['nom']} — {code}...")
            time.sleep(0.1)

        if features_alea:
            resultats[alea_key] = features_alea

    return resultats


# =============================================================================
# Cache & téléchargement BD TOPO
# =============================================================================

def cache_lire_index() -> dict:
    if CACHE_INDEX.exists():
        with open(CACHE_INDEX, encoding="utf-8") as f:
            return json.load(f)
    return {}


def cache_ecrire_index(index: dict):
    with open(CACHE_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def cache_est_valide(dept: str) -> Path | None:
    index = cache_lire_index()
    entree = index.get(dept)
    if not entree:
        return None
    archive = Path(entree["chemin"])
    if not archive.exists():
        return None
    taille = archive.stat().st_size
    if entree.get("taille_octets") and taille != entree["taille_octets"]:
        return None
    return archive


def trouver_url_bdtopo(dept: str) -> str | None:
    millesimes = ["2024-09-15", "2024-06-15", "2024-03-15", "2023-09-15"]
    for mil in millesimes:
        url = (f"https://data.geopf.fr/telechargement/download/BD-TOPO/"
               f"BD-TOPO_3-3__SHP_LAMB93_D0{dept}_{mil}/"
               f"BD-TOPO_3-3__SHP_LAMB93_D0{dept}_{mil}.7z")
        try:
            r = requests.head(url, timeout=10)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None


# =============================================================================
# Génération du GeoPackage territoire
# =============================================================================

def generer_geopackage(territoire: dict, couches_voulues: dict,
                       aleas_voulus: list, progress_cb=None, log_cb=None) -> Path | None:
    """
    Génère le GeoPackage complet pour un territoire.
    Retourne le chemin du .gpkg créé.
    """

    def log(msg):
        if log_cb:
            log_cb(msg)

    codes = [c["code"] for c in territoire["communes"]]
    dept  = territoire["departement"]
    nom   = territoire["nom"]
    nom_safe = nom.replace(" ", "_").replace("/", "-")

    # Structure dossiers
    dossier_terr = DATA_DIR / f"PICS_{nom_safe}"
    dossier_qgis = dossier_terr / "Qgis"
    dossier_docs = dossier_terr / "documents" / "PICS"
    dossier_tmp  = dossier_terr / "_tmp"
    for d in [dossier_qgis, dossier_docs, dossier_tmp]:
        d.mkdir(parents=True, exist_ok=True)

    gpkg_path = dossier_qgis / f"{nom_safe}.gpkg"
    if gpkg_path.exists():
        gpkg_path.unlink()

    toutes_couches = {}

    # ── 1. Limites administratives ──────────────────────────
    log("Récupération des communes...")
    gdf_communes = recuperer_geometries_communes(
        codes,
        progress_cb=lambda i, n, msg: progress_cb(i, n * 6, f"Communes : {msg}") if progress_cb else None
    )

    if gdf_communes is None:
        log("❌ Impossible de récupérer les communes.")
        return None

    noms_map = {c["code"]: c["nom"] for c in territoire["communes"]}
    if "code" in gdf_communes.columns:
        gdf_communes["nom_config"] = gdf_communes["code"].map(noms_map)

    perimetre = gdf_communes.dissolve().reset_index(drop=True)
    perimetre["nom"] = nom
    perimetre["code_epci"] = territoire.get("code_epci", "")
    perimetre["nb_communes"] = len(codes)

    toutes_couches["communes"] = gdf_communes
    toutes_couches["perimetre_intercommunal"] = perimetre

    # Calcul bbox
    geom_union    = unary_union(gdf_communes.geometry)
    geom_buf      = geom_union.buffer(territoire.get("buffer_km", 2) * 1000)
    bbox_l93      = geom_buf.bounds
    xmin, ymin, xmax, ymax = bbox_l93

    gdf_buf_wgs = gpd.GeoDataFrame(geometry=[geom_buf], crs="EPSG:2154").to_crs("EPSG:4326")
    bbox_wgs84  = gdf_buf_wgs.total_bounds

    log(f"✓ {len(gdf_communes)} communes | bbox calculée")

    # ── 2. Hydrologie SANDRE ────────────────────────────────
    if couches_voulues.get("hydrologie", True):
        log("Hydrologie (SANDRE)...")
        bx, by, bX, bY = bbox_wgs84
        for nom_hydro, typename in [("cours_eau", "CoursEau"), ("plans_eau", "PlanEau")]:
            try:
                params = {
                    "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
                    "TYPENAME": typename, "OUTPUTFORMAT": "application/json",
                    "SRSNAME": "EPSG:4326",
                    "BBOX": f"{by},{bx},{bY},{bX},EPSG:4326",
                    "COUNT": "5000",
                }
                r = requests.get("https://services.sandre.eaufrance.fr/geo/hyd",
                                 params=params, timeout=45)
                r.raise_for_status()
                dest = dossier_tmp / f"{nom_hydro}.geojson"
                dest.write_bytes(r.content)
                gdf = gpd.read_file(dest)
                if len(gdf) > 0:
                    gdf = gdf.to_crs("EPSG:2154")
                    toutes_couches[nom_hydro] = gdf
                    log(f"✓ {nom_hydro} : {len(gdf)} objets")
            except Exception as e:
                log(f"⚠ {nom_hydro} non disponible : {e}")

    # ── 3. Aléas Géorisques ─────────────────────────────────
    if aleas_voulus:
        log(f"Aléas Géorisques ({len(aleas_voulus)} couches)...")
        step_gr = [0]
        total_gr = len(aleas_voulus) * len(codes)

        def pb_gr(s, t, msg):
            step_gr[0] = s
            if progress_cb:
                progress_cb(s, t, f"Géorisques : {msg}")

        aleas_data = recuperer_aleas_territoire(codes, aleas_voulus, pb_gr)

        for alea_key, features in aleas_data.items():
            config = ALEAS_CONFIG[alea_key]
            log(f"✓ {config['nom']} : {len(features)} entrées")
            # Stockage brut — la conversion GDF est faite à l'export
            territoire_obj = territoire.copy()
            territoire_obj[f"aleas_{alea_key}"] = features

        # On stocke les données brutes pour l'export cartes
        st_key = f"aleas_{nom_safe}"
        import streamlit as st
        st.session_state[st_key] = aleas_data

    # ── 4. BD TOPO ──────────────────────────────────────────
    bdtopo_voulu = {k: couches_voulues.get(k, True)
                    for k in ["routes", "batiments", "vegetation"]}

    if any(bdtopo_voulu.values()):
        log(f"BD TOPO département {dept}...")

        archive = cache_est_valide(dept)
        if archive:
            log(f"✓ BD TOPO D{dept} en cache ({archive.stat().st_size / 1e6:.0f} Mo)")
        else:
            log(f"Téléchargement BD TOPO D{dept}...")
            url = trouver_url_bdtopo(dept)
            if not url:
                log("❌ BD TOPO introuvable pour ce département.")
            else:
                archive = CACHE_DIR / f"bdtopo_{dept}.7z"
                try:
                    r = requests.get(url, stream=True, timeout=300)
                    r.raise_for_status()
                    taille = int(r.headers.get("content-length", 0))
                    downloaded = 0
                    with open(archive, "wb") as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_cb and taille:
                                progress_cb(downloaded, taille, "Téléchargement BD TOPO...")
                    index = cache_lire_index()
                    index[dept] = {
                        "chemin": str(archive), "url": url,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "taille_octets": archive.stat().st_size,
                    }
                    cache_ecrire_index(index)
                    log(f"✓ BD TOPO D{dept} téléchargée et mise en cache")
                except Exception as e:
                    log(f"❌ Téléchargement BD TOPO échoué : {e}")
                    archive = None

        if archive:
            extract_dir = CACHE_DIR / f"bdtopo_{dept}_extracted"
            marker = extract_dir / ".ok"
            if not marker.exists():
                log("Décompression BD TOPO...")
                extract_dir.mkdir(exist_ok=True)
                try:
                    import py7zr
                    with py7zr.SevenZipFile(archive, mode="r") as z:
                        z.extractall(path=extract_dir)
                    marker.touch()
                    log("✓ Décompression OK")
                except Exception as e:
                    log(f"❌ Décompression échouée : {e}")

            if marker.exists():
                mapping = {
                    "routes":        "TRONCON_DE_ROUTE.shp",
                    "voies_ferrees": "TRONCON_DE_VOIE_FERREE.shp",
                    "batiments":     "BATIMENT.shp",
                    "vegetation":    "ZONE_DE_VEGETATION.shp",
                }
                for couche, shp_name in mapping.items():
                    config_key = "routes" if couche == "voies_ferrees" else couche
                    if not bdtopo_voulu.get(config_key, True):
                        continue
                    shp_files = list(extract_dir.rglob(shp_name))
                    if not shp_files:
                        continue
                    try:
                        gdf = gpd.read_file(shp_files[0], bbox=(xmin, ymin, xmax, ymax))
                        if len(gdf) > 0:
                            if gdf.crs and gdf.crs.to_epsg() != 2154:
                                gdf = gdf.to_crs("EPSG:2154")
                            toutes_couches[couche] = gdf
                            log(f"✓ {couche} : {len(gdf)} objets")
                    except Exception as e:
                        log(f"⚠ {couche} : {e}")

    # ── 5. Sauvegarde GeoPackage ────────────────────────────
    log("Sauvegarde GeoPackage...")
    nb_ok = 0
    for nom_couche, gdf in toutes_couches.items():
        if gdf is None or len(gdf) == 0:
            continue
        try:
            if gdf.crs and gdf.crs.to_epsg() != 2154:
                gdf = gdf.to_crs("EPSG:2154")
            gdf.columns = [c[:60] for c in gdf.columns]
            gdf = gdf[gdf.geometry.notna()]
            gdf["geometry"] = gdf["geometry"].buffer(0)
            gdf.to_file(gpkg_path, layer=nom_couche, driver="GPKG")
            nb_ok += 1
        except Exception as e:
            log(f"⚠ {nom_couche} non sauvegardé : {e}")

    # Nettoyage tmp
    shutil.rmtree(dossier_tmp, ignore_errors=True)

    log(f"✅ GeoPackage généré — {nb_ok} couches | {gpkg_path}")
    return gpkg_path
