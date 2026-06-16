"""Page Export — GeoPackage QGIS + PDF des cartes."""
import io
import json
import zipfile
import requests
import geopandas as gpd
import streamlit as st
from pathlib import Path
from datetime import datetime
from components.style import C, topbar

def render():
    actif = st.session_state.get("territoire_actif")
    topbar(actif)

    if not actif:
        st.warning("Aucun territoire actif.")
        return

    config  = st.session_state.territoires[actif]
    donnees = st.session_state.donnees_chargees.get(actif, {})
    codes   = [c["code"] for c in config.get("communes", [])]
    nom_safe = actif.replace(" ","_").replace("/","-")

    st.markdown('<p class="mapos-eyebrow">Livrables</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="mapos-section-title">Export — {actif}</h2>', unsafe_allow_html=True)

    nb_couches = len(donnees)
    nb_ok      = sum(1 for v in donnees.values() if v.get("nb",0) > 0)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Couches disponibles", f"{nb_ok}/{nb_couches}")
    with col2: st.metric("Communes", len(codes))
    with col3: st.metric("Format", "Lambert 93 · EPSG:2154")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Export GeoPackage
    st.markdown(f'<div class="mapos-eyebrow">GeoPackage QGIS</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mapos-card" style="margin-bottom:1rem">
        <div class="mapos-card-title">📦 {nom_safe}.gpkg</div>
        <div class="mapos-body" style="margin:0.5rem 0">
            Fichier GeoPackage contenant toutes les couches disponibles,
            directement importable dans QGIS. Projection Lambert 93 (EPSG:2154).
        </div>
        <div style="margin-top:0.75rem;display:flex;flex-wrap:wrap;gap:6px">
            {''.join(f'<span class="badge badge-info">{k}</span>' for k,v in donnees.items() if v.get("nb",0)>0)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if nb_ok == 0:
        st.info("Aucune donnée disponible. Allez dans **Aléas** pour télécharger les données.")
    else:
        if st.button("⬇  Générer et télécharger le GeoPackage", type="primary"):
            with st.spinner("Génération du GeoPackage..."):
                gpkg_bytes = _generer_gpkg(codes, donnees, actif)
                if gpkg_bytes:
                    st.download_button(
                        f"⬇ Télécharger {nom_safe}.gpkg",
                        data=gpkg_bytes,
                        file_name=f"{nom_safe}.gpkg",
                        mime="application/geopackage+sqlite3",
                    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Export ZIP complet
    st.markdown(f'<div class="mapos-eyebrow">Archive complète</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mapos-card">
        <div class="mapos-card-title">📁 Structure du projet PICS</div>
        <div class="mapos-body" style="margin:0.5rem 0">
            Archive ZIP avec la structure de dossiers complète pour l'élaboration du PICS.
        </div>
        <div style="background:{C['bg']};border-radius:8px;padding:12px;
                    margin-top:0.75rem;font-size:12px;font-family:monospace;
                    color:{C['textMuted']};line-height:1.8">
            PICS_{nom_safe}/<br>
            ├── Qgis/{nom_safe}.gpkg<br>
            ├── documents/PICS/<br>
            └── README.txt
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⬇  Télécharger l'archive ZIP complète"):
        with st.spinner("Génération de l'archive..."):
            zip_bytes = _generer_zip(codes, donnees, actif, config, nom_safe)
            if zip_bytes:
                st.download_button(
                    f"⬇ PICS_{nom_safe}.zip",
                    data=zip_bytes,
                    file_name=f"PICS_{nom_safe}.zip",
                    mime="application/zip",
                )


def _generer_gpkg(codes: list, donnees: dict, actif: str) -> bytes | None:
    try:
        # Communes
        geometries = []
        for code in codes:
            r = requests.get(
                f"https://geo.api.gouv.fr/communes/{code}?fields=nom,code,geometry&format=geojson&geometry=contour",
                timeout=15)
            if r.ok:
                geometries.append(r.json())

        buf = io.BytesIO()

        if geometries:
            gdf_com = gpd.GeoDataFrame.from_features(geometries, crs="EPSG:4326")
            gdf_com = gdf_com.to_crs(epsg=2154)
            gdf_com.to_file(buf, layer="communes", driver="GPKG", engine="pyogrio")

            perim = gdf_com.dissolve().reset_index(drop=True)
            perim["nom_epci"] = actif
            perim.to_file(buf, layer="perimetre_intercommunal", driver="GPKG", engine="pyogrio")

        # Couches aléas (geojson)
        for cle, meta in donnees.items():
            if meta.get("type") == "geojson" and meta.get("data") and meta.get("nb",0) > 0:
                try:
                    gdf = gpd.read_file(io.BytesIO(meta["data"].encode()), engine="pyogrio")
                    if len(gdf) > 0:
                        gdf = gdf.to_crs(epsg=2154)
                        gdf.to_file(buf, layer=cle, driver="GPKG", engine="pyogrio")
                except Exception:
                    pass

        buf.seek(0)
        return buf.read()
    except Exception as e:
        st.error(f"Erreur GeoPackage : {e}")
        return None


def _generer_zip(codes, donnees, actif, config, nom_safe) -> bytes | None:
    try:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # README
            readme = _generer_readme(actif, config, donnees)
            zf.writestr(f"PICS_{nom_safe}/README.txt", readme)

            # GeoPackage
            gpkg = _generer_gpkg(codes, donnees, actif)
            if gpkg:
                zf.writestr(f"PICS_{nom_safe}/Qgis/{nom_safe}.gpkg", gpkg)

            # Placeholder documents
            zf.writestr(f"PICS_{nom_safe}/documents/PICS/.gitkeep", "")

        buf.seek(0)
        return buf.read()
    except Exception as e:
        st.error(f"Erreur ZIP : {e}")
        return None


def _generer_readme(actif, config, donnees) -> str:
    date = datetime.now().strftime("%d/%m/%Y à %H:%M")
    communes = config.get("communes", [])
    couches_ok = [k for k,v in donnees.items() if v.get("nb",0)>0]
    return f"""PICS — {actif}
{'='*60}
Généré par MapOS (Sildaro) le {date}

TERRITOIRE
----------
  Nom           : {actif}
  Département   : {config.get('departement','?')}
  Code EPCI     : {config.get('code_epci','—')}
  Communes      : {len(communes)}

COMMUNES MEMBRES
----------------
{''.join(f"  {c['code']}  {c['nom']}" + chr(10) for c in communes)}
DONNÉES SIG DISPONIBLES
-----------------------
  Fichier  : Qgis/{actif.replace(' ','_').replace('/','‑')}.gpkg
  Couches  : {', '.join(couches_ok) if couches_ok else 'aucune'}

STRUCTURE DU PROJET
-------------------
  Qgis/               → Données cartographiques (.gpkg)
  documents/PICS/     → Documents du PICS à compléter

SOURCES
-------
  Limites communes  : API Géo (geo.api.gouv.fr)
  Aléas             : Géorisques (georisques.gouv.fr)
  Hydrologie        : SANDRE / BD Carthage
  Fond de carte     : IGN Géoplateforme

OUVRIR DANS QGIS
----------------
  Glisser-déposer le fichier .gpkg dans QGIS
  Toutes les couches sont en Lambert 93 (EPSG:2154)
"""
