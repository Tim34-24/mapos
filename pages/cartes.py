"""Page Cartes — génération des cartes thématiques avec matplotlib + contextily."""
import io
import json
import requests
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import contextily as ctx
import streamlit as st
from shapely.geometry import shape, box
from shapely.ops import unary_union
from components.style import C, topbar

CARTES_CONFIG = [
    {
        "id": "territoire",
        "nom": "Carte du territoire",
        "icon": "📍",
        "description": "Périmètre intercommunal, communes membres, axes routiers.",
        "couches_requises": [],
        "badge": "badge-ok",
    },
    {
        "id": "inondation",
        "nom": "Risque inondation",
        "icon": "💧",
        "description": "Zones PPRI, AZI, remontées de nappe, cours d'eau.",
        "couches_requises": ["inondation_ppri", "cours_eau"],
        "badge": "badge-info",
    },
    {
        "id": "mvt_terrain",
        "nom": "Mouvements de terrain",
        "icon": "⛰️",
        "description": "Zones PPRN, cavités souterraines, aléa RGA.",
        "couches_requises": ["mvt_terrain", "cavites", "rga"],
        "badge": "badge-warn",
    },
    {
        "id": "industriel",
        "nom": "Risque industriel & TMD",
        "icon": "🏭",
        "description": "Sites ICPE, canalisations de matières dangereuses.",
        "couches_requises": ["icpe", "canalisations"],
        "badge": "badge-alert",
    },
    {
        "id": "aleas_synthetique",
        "nom": "Carte de synthèse des aléas",
        "icon": "🗺️",
        "description": "Superposition de tous les aléas réglementaires.",
        "couches_requises": [],
        "badge": "badge-neu",
    },
]

COULEURS_ALEAS = {
    "inondation_ppri":   ("#1a6bb5", "#85B7EB", "Zones PPRI"),
    "inondation_azi":    ("#1a9fd4", "#a8d8f0", "Atlas zones inondables"),
    "inondation_nappe":  ("#5b9ec9", "#c5e0f0", "Remontées de nappe"),
    "mvt_terrain":       ("#8B4513", "#D2691E", "Mouvements de terrain"),
    "cavites":           ("#4a3728", "#8B6960", "Cavités souterraines"),
    "rga":               ("#b8860b", "#DAA520", "Retrait-gonflement argiles"),
    "icpe":              ("#8B0000", "#E24B4A", "Sites ICPE"),
    "canalisations":     ("#FF6600", "#FFA500", "Canalisations TMD"),
    "cours_eau":         ("#0066CC", "#4da6ff", "Cours d'eau"),
}


def render():
    actif = st.session_state.get("territoire_actif")
    topbar(actif)

    if not actif:
        st.warning("Aucun territoire actif.")
        return

    config  = st.session_state.territoires[actif]
    donnees = st.session_state.donnees_chargees.get(actif, {})
    codes   = [c["code"] for c in config.get("communes", [])]

    st.markdown('<p class="mapos-eyebrow">Génération cartographique</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="mapos-section-title">Cartes — {actif}</h2>', unsafe_allow_html=True)

    if not donnees:
        st.info("Aucune donnée chargée. Allez dans **Aléas** pour télécharger les données d'abord.")
        if st.button("→ Aller aux Aléas"):
            st.session_state.page = "aleas"
            st.rerun()
        return

    # Options de génération
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        format_papier = st.selectbox("Format", ["A4", "A3"], index=1)
    with col_opt2:
        orientation  = st.selectbox("Orientation", ["Paysage", "Portrait"])
    with col_opt3:
        fond_carte   = st.selectbox("Fond de carte", ["IGN Plan", "OpenStreetMap", "Aucun"])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<h3 style="font-size:16px;font-weight:500;color:{C["text"]};margin-bottom:1rem">Cartes disponibles</h3>', unsafe_allow_html=True)

    for carte in CARTES_CONFIG:
        couches_ok = all(c in donnees for c in carte["couches_requises"])
        dispo = couches_ok or not carte["couches_requises"]

        col_info, col_btn = st.columns([5, 1])
        with col_info:
            manquantes_html = ""
            if not dispo:
                manquantes = [c for c in carte["couches_requises"] if c not in donnees]
                manquantes_html = f'<span class="badge badge-alert">Données manquantes : {", ".join(manquantes)}</span>'

            st.markdown(f"""
            <div class="mapos-card" style="margin-bottom:8px;opacity:{'1' if dispo else '0.5'}">
                <div style="display:flex;align-items:center;gap:12px">
                    <span style="font-size:22px">{carte['icon']}</span>
                    <div style="flex:1">
                        <div class="mapos-card-title">{carte['nom']}</div>
                        <div class="mapos-small" style="margin-top:2px">{carte['description']}</div>
                        {manquantes_html}
                    </div>
                    <span class="badge {carte['badge']}">{'Prêt' if dispo else 'Incomplet'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
            if st.button("Générer", key=f"gen_{carte['id']}", disabled=not dispo):
                with st.spinner(f"Génération de {carte['nom']}..."):
                    fig = _generer_carte(
                        carte_id=carte["id"],
                        actif=actif,
                        codes=codes,
                        donnees=donnees,
                        format_papier=format_papier,
                        orientation=orientation,
                        fond_carte=fond_carte,
                    )
                    if fig:
                        st.pyplot(fig, use_container_width=True)
                        buf = io.BytesIO()
                        fig.savefig(buf, format="pdf", bbox_inches="tight", dpi=200)
                        buf.seek(0)
                        nom_fichier = f"MapOS_{actif.replace(' ','_')}_{carte['id']}.pdf"
                        st.download_button(
                            f"⬇ Télécharger PDF — {carte['nom']}",
                            data=buf,
                            file_name=nom_fichier,
                            mime="application/pdf",
                            key=f"dl_{carte['id']}",
                        )
                        plt.close(fig)
            st.markdown("</div>", unsafe_allow_html=True)


def _generer_carte(carte_id, actif, codes, donnees, format_papier, orientation, fond_carte):
    """Génère une figure matplotlib pour la carte demandée."""
    try:
        # Dimensions en pouces
        if format_papier == "A3":
            w, h = (16.53, 11.69) if orientation == "Paysage" else (11.69, 16.53)
        else:
            w, h = (11.69, 8.27) if orientation == "Paysage" else (8.27, 11.69)

        fig, ax = plt.subplots(1, 1, figsize=(w, h))
        fig.patch.set_facecolor("#1C1C1A")
        ax.set_facecolor("#272724")

        # Récupération géométries communes
        gdf_communes = _recuperer_communes_gdf(codes)
        if gdf_communes is None or len(gdf_communes) == 0:
            st.error("Impossible de récupérer les géométries des communes.")
            return None

        gdf_communes = gdf_communes.to_crs(epsg=3857)
        perimetre    = gdf_communes.dissolve()

        # Extent avec marge
        bounds  = perimetre.total_bounds
        marge   = (bounds[2]-bounds[0]) * 0.08
        ax.set_xlim(bounds[0]-marge, bounds[2]+marge)
        ax.set_ylim(bounds[1]-marge, bounds[3]+marge)

        legend_patches = []

        # ── Fond de carte ──────────────────────────────────────────
        if fond_carte != "Aucun":
            try:
                source = ctx.providers.GeoportailFrance.plan if fond_carte == "IGN Plan" else ctx.providers.OpenStreetMap.Mapnik
                ctx.add_basemap(ax, source=source, zoom="auto", alpha=0.5)
            except Exception:
                pass

        # ── Périmètre intercommunal ─────────────────────────────────
        perimetre.boundary.plot(ax=ax, color="#E24B4A", linewidth=2, zorder=5)
        gdf_communes.boundary.plot(ax=ax, color="rgba(232,230,225,0.3)",
                                   linewidth=0.6, zorder=4, edgecolor="#7A7873")
        gdf_communes.plot(ax=ax, color="#272724", alpha=0.4, zorder=3)

        legend_patches.append(mpatches.Patch(facecolor="#272724", edgecolor="#E24B4A",
                                              linewidth=2, label="Périmètre CCGM"))

        # ── Couches spécifiques selon la carte ─────────────────────
        if carte_id == "inondation":
            couches_inond = ["inondation_ppri","inondation_azi","inondation_nappe","cours_eau"]
            for cle in couches_inond:
                if cle in donnees and donnees[cle].get("data") and donnees[cle].get("type") == "geojson":
                    try:
                        gdf = gpd.read_file(io.BytesIO(donnees[cle]["data"].encode()), engine="pyogrio")
                        if len(gdf) > 0:
                            gdf = gdf.to_crs(epsg=3857)
                            couleur, _, label = COULEURS_ALEAS.get(cle, ("#888","#aaa","Aléa"))
                            gdf.plot(ax=ax, color=couleur, alpha=0.5, zorder=6)
                            legend_patches.append(mpatches.Patch(color=couleur, alpha=0.7, label=label))
                    except Exception:
                        pass

        elif carte_id == "mvt_terrain":
            for cle in ["mvt_terrain","cavites","rga"]:
                if cle in donnees and donnees[cle].get("data") and donnees[cle].get("type") == "geojson":
                    try:
                        gdf = gpd.read_file(io.BytesIO(donnees[cle]["data"].encode()), engine="pyogrio")
                        if len(gdf) > 0:
                            gdf = gdf.to_crs(epsg=3857)
                            couleur, _, label = COULEURS_ALEAS.get(cle, ("#888","#aaa","Aléa"))
                            gdf.plot(ax=ax, color=couleur, alpha=0.6, zorder=6)
                            legend_patches.append(mpatches.Patch(color=couleur, alpha=0.7, label=label))
                    except Exception:
                        pass

        elif carte_id == "industriel":
            for cle in ["canalisations","icpe"]:
                if cle in donnees and donnees[cle].get("data"):
                    if donnees[cle].get("type") == "geojson":
                        try:
                            gdf = gpd.read_file(io.BytesIO(donnees[cle]["data"].encode()), engine="pyogrio")
                            if len(gdf) > 0:
                                gdf = gdf.to_crs(epsg=3857)
                                couleur, _, label = COULEURS_ALEAS.get(cle, ("#888","#aaa","Aléa"))
                                gdf.plot(ax=ax, color=couleur, alpha=0.7, zorder=6)
                                legend_patches.append(mpatches.Patch(color=couleur, alpha=0.8, label=label))
                        except Exception:
                            pass
                    elif donnees[cle].get("type") == "json":
                        # Points ICPE depuis JSON
                        data_list = donnees[cle].get("data", [])
                        pts = [(d.get("longitude"), d.get("latitude")) for d in data_list if d.get("longitude") and d.get("latitude")]
                        if pts:
                            xs, ys = zip(*pts)
                            gdf_pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(xs, ys), crs="EPSG:4326")
                            gdf_pts = gdf_pts.to_crs(epsg=3857)
                            ax.scatter(gdf_pts.geometry.x, gdf_pts.geometry.y,
                                       c="#E24B4A", s=40, zorder=8, marker="^",
                                       edgecolors="#F09595", linewidth=0.5, alpha=0.9)
                            legend_patches.append(mpatches.Line2D([0],[0], marker="^", color="w",
                                markerfacecolor="#E24B4A", markersize=8, label="Sites ICPE"))

        elif carte_id == "aleas_synthetique":
            for cle, (couleur, _, label) in COULEURS_ALEAS.items():
                if cle in donnees and donnees[cle].get("data") and donnees[cle].get("type") == "geojson":
                    try:
                        gdf = gpd.read_file(io.BytesIO(donnees[cle]["data"].encode()), engine="pyogrio")
                        if len(gdf) > 0:
                            gdf = gdf.to_crs(epsg=3857)
                            gdf.plot(ax=ax, color=couleur, alpha=0.45, zorder=6)
                            legend_patches.append(mpatches.Patch(color=couleur, alpha=0.7, label=label))
                    except Exception:
                        pass

        # ── Labels communes ─────────────────────────────────────────
        for _, row in gdf_communes.iterrows():
            centroid = row.geometry.centroid
            nom = row.get("nom") or row.get("NOM") or ""
            if nom:
                ax.annotate(nom, xy=(centroid.x, centroid.y),
                    ha="center", va="center", fontsize=6.5,
                    color="#E8E6E1", fontweight="normal",
                    path_effects=[pe.withStroke(linewidth=2, foreground="#1C1C1A")])

        # ── Légende ─────────────────────────────────────────────────
        if legend_patches:
            leg = ax.legend(
                handles=legend_patches,
                loc="lower left", frameon=True,
                facecolor="#272724", edgecolor="rgba(232,230,225,0.2)",
                labelcolor="#E8E6E1", fontsize=8,
                title_fontsize=9, framealpha=0.92,
            )

        # ── Habillage ───────────────────────────────────────────────
        nom_carte = next((c["nom"] for c in CARTES_CONFIG if c["id"]==carte_id), carte_id)
        ax.set_title(
            f"MapOS · {actif} — {nom_carte}",
            color="#E8E6E1", fontsize=12, fontweight="normal",
            loc="left", pad=12, fontfamily="DejaVu Sans",
        )
        ax.text(0.99, 0.01,
            "Sources : IGN BD TOPO · Géorisques · SANDRE\nProjection : EPSG:3857 · MapOS par Sildaro",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.5, color="#4A4946",)

        ax.set_axis_off()
        fig.tight_layout(pad=0.5)
        return fig

    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")
        return None


def _recuperer_communes_gdf(codes: list) -> gpd.GeoDataFrame | None:
    geometries = []
    for code in codes:
        try:
            r = requests.get(
                f"https://geo.api.gouv.fr/communes/{code}?fields=nom,code,geometry&format=geojson&geometry=contour",
                timeout=15)
            if r.ok:
                geometries.append(r.json())
        except Exception:
            pass
    if not geometries:
        return None
    return gpd.GeoDataFrame.from_features(geometries, crs="EPSG:4326")
