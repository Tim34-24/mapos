"""
Page Exports — Génération de cartes PDF et téléchargements
"""

import streamlit as st
import io
from pathlib import Path
from core.state import get_territoire_actif, charger_territoires
from core.territoire import ALEAS_CONFIG


def render():
    territoires = charger_territoires()
    if not territoires:
        st.markdown("""
        <div class="mapos-card" style="text-align:center; padding: 2.5rem;">
            <div style="font-size: 14px; color: #7A7873;">
                Aucun territoire configuré.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="card-eyebrow">EXPORTS</div>
        <div class="page-title">Cartes & fichiers</div>
        <div class="page-subtitle">
            Téléchargez le GeoPackage pour QGIS et exportez les cartes thématiques en PDF.
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
        key="exp_select"
    )
    if choix != st.session_state.get("territoire_actif"):
        st.session_state.territoire_actif = choix
        st.rerun()

    territoire = get_territoire_actif()
    if not territoire:
        return

    nom_safe = territoire["nom"].replace(" ", "_").replace("/", "-")
    dossier  = Path(__file__).parent.parent / "data" / f"PICS_{nom_safe}"
    gpkg     = dossier / "Qgis" / f"{nom_safe}.gpkg"

    # ── Statut GeoPackage ────────────────────────────────────
    if not gpkg.exists():
        st.markdown("""
        <div class="mapos-card" style="border-color: rgba(226,75,74,0.3);">
            <div style="font-size: 14px; color: #F09595;">
                ⚠️ Aucun GeoPackage disponible pour ce territoire.<br>
                <span style="color: #7A7873;">Allez dans <b style="color: #E8E6E1">Génération données</b>
                pour créer les données SIG.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚙️ Aller à la génération", type="primary"):
            st.session_state.page = "generation"
            st.rerun()
        return

    taille_mo = gpkg.stat().st_size / 1e6

    st.markdown(f"""
    <div class="mapos-card" style="border-color: rgba(29,158,117,0.3); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 14px; font-weight: 500; color: #5DCAA5;">
                    ✓ GeoPackage disponible
                </div>
                <div style="font-size: 12px; color: #7A7873; margin-top: 4px;">
                    {gpkg.name} · {taille_mo:.1f} Mo
                </div>
            </div>
            <span class="badge badge-ok">QGIS ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    # ── Téléchargement GeoPackage ────────────────────────────
    with col_left:
        st.markdown('<div class="section-title">Fichiers</div>', unsafe_allow_html=True)
        st.markdown('<div class="mapos-card-lg">', unsafe_allow_html=True)

        with open(gpkg, "rb") as f:
            st.download_button(
                label=f"📦  Télécharger {gpkg.name}",
                data=f.read(),
                file_name=gpkg.name,
                mime="application/geopackage+sqlite3",
                use_container_width=True,
                type="primary",
            )

        st.markdown("""
        <div style="font-size: 11px; color: #4A4946; margin-top: 10px; line-height: 1.7;">
            Glisser-déposer dans QGIS pour charger toutes les couches.<br>
            Projection : Lambert 93 (EPSG:2154)
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Structure du projet ──────────────────────────────
        st.markdown('<div class="section-title" style="margin-top: 1rem;">Structure du projet</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="mapos-card-lg">
            <div style="font-family: monospace; font-size: 12px; color: #7A7873; line-height: 2;">
                <span style="color: #E8E6E1">PICS_{nom_safe}/</span><br>
                &nbsp;&nbsp;├── <span style="color: #85B7EB">Qgis/</span><br>
                &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── {nom_safe}.gpkg<br>
                &nbsp;&nbsp;└── <span style="color: #85B7EB">documents/</span><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── <span style="color: #85B7EB">PICS/</span><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── ← cartes PDF ici
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Export cartes PDF ────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-title">Cartes thématiques</div>', unsafe_allow_html=True)

        cartes_disponibles = [
            {
                "id": "territoire",
                "nom": "Carte du territoire",
                "desc": "Périmètre CCGM, communes membres, routes principales",
                "icone": "🗺️",
                "couches": ["perimetre_intercommunal", "communes", "routes"],
            },
            {
                "id": "inondation",
                "nom": "Carte inondation",
                "desc": "PPRI, cours d'eau, zones à risque, CATNAT",
                "icone": "💧",
                "couches": ["cours_eau", "plans_eau", "ppri", "catnat"],
            },
            {
                "id": "mouvements",
                "nom": "Mouvements de terrain",
                "desc": "PPRN, cavités souterraines, marnières",
                "icone": "⛰️",
                "couches": ["pprn_mouvements", "cavites"],
            },
            {
                "id": "vegetation",
                "nom": "Végétation & feux",
                "desc": "Massifs forestiers, interface bâti-forêt",
                "icone": "🌲",
                "couches": ["vegetation", "batiments"],
            },
            {
                "id": "icpe_tmd",
                "nom": "Risques industriels & TMD",
                "desc": "ICPE, canalisations, axes de transport MD",
                "icone": "🏭",
                "couches": ["icpe", "canalisations", "routes"],
            },
            {
                "id": "enjeux",
                "nom": "Carte des enjeux",
                "desc": "Bâtiments sensibles, ERP, axes structurants",
                "icone": "🎯",
                "couches": ["batiments", "routes", "voies_ferrees"],
            },
            {
                "id": "atlas",
                "nom": "Atlas communal (11 cartes)",
                "desc": "Une carte par commune membre au même format",
                "icone": "📚",
                "couches": ["communes", "perimetre_intercommunal"],
            },
        ]

        # Options de format
        col_fmt1, col_fmt2, col_fmt3 = st.columns(3)
        with col_fmt1:
            fmt = st.selectbox("Format", ["A3", "A4"], key="exp_format")
        with col_fmt2:
            orient = st.selectbox("Orientation", ["Paysage", "Portrait"], key="exp_orient")
        with col_fmt3:
            fond = st.selectbox("Fond de carte", ["Plan IGN", "Ortho IGN", "OSM"], key="exp_fond")

        st.markdown('<div style="height: 0.5rem"></div>', unsafe_allow_html=True)

        for carte in cartes_disponibles:
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                st.markdown(f"""
                <div style="padding: 8px 0; border-bottom: 0.5px solid rgba(232,230,225,0.06);">
                    <div style="font-size: 13px; color: #E8E6E1;">
                        {carte['icone']} {carte['nom']}
                    </div>
                    <div style="font-size: 11px; color: #7A7873; margin-top: 2px;">
                        {carte['desc']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_c2:
                if st.button("PDF", key=f"pdf_{carte['id']}", use_container_width=True):
                    with st.spinner(f"Génération {carte['nom']}..."):
                        pdf_bytes = _generer_carte_pdf(
                            territoire, gpkg, carte, fmt, orient, fond
                        )
                        if pdf_bytes:
                            nom_fichier = f"{nom_safe}_{carte['id']}.pdf"
                            st.download_button(
                                label=f"⬇ {nom_fichier}",
                                data=pdf_bytes,
                                file_name=nom_fichier,
                                mime="application/pdf",
                                key=f"dl_{carte['id']}",
                                use_container_width=True,
                            )

        # Bouton tout exporter
        st.markdown('<div style="height: 0.75rem"></div>', unsafe_allow_html=True)
        if st.button("📦  Exporter toutes les cartes", type="primary", use_container_width=True):
            _exporter_toutes(territoire, gpkg, cartes_disponibles, fmt, orient, fond, nom_safe)


def _generer_carte_pdf(territoire: dict, gpkg: Path, carte: dict,
                       format_papier: str, orientation: str, fond: str) -> bytes | None:
    """Génère une carte PDF via matplotlib + contextily."""
    try:
        import geopandas as gpd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import contextily as ctx
        from matplotlib.patches import FancyArrowPatch
        import io

        # Dimensions papier en pouces
        dims = {
            "A4": {"Portrait": (8.27, 11.69), "Paysage": (11.69, 8.27)},
            "A3": {"Portrait": (11.69, 16.54), "Paysage": (16.54, 11.69)},
        }
        figsize = dims.get(format_papier, dims["A4"]).get(orientation, (11.69, 8.27))

        fig, ax = plt.subplots(1, 1, figsize=figsize, facecolor="#1C1C1A")
        ax.set_facecolor("#1C1C1A")
        ax.tick_params(colors="#7A7873")
        for spine in ax.spines.values():
            spine.set_edgecolor("#4A4946")

        # Fond de carte
        sources_fond = {
            "Plan IGN":   "https://wxs.ign.fr/decouverte/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/png&STYLE=normal",
            "Ortho IGN":  ctx.providers.GeoportailFrance.orthos,
            "OSM":        ctx.providers.OpenStreetMap.Mapnik,
        }

        # Chargement des couches disponibles dans le gpkg
        import fiona
        couches_gpkg = fiona.listlayers(str(gpkg))

        couleurs = {
            "perimetre_intercommunal": {"color": "none", "edgecolor": "#E24B4A", "linewidth": 2.5, "zorder": 10},
            "communes":                {"color": "none", "edgecolor": "rgba(232,230,225,0.3)", "linewidth": 0.8, "zorder": 9},
            "cours_eau":               {"color": "#1a6eb5", "linewidth": 1.5, "zorder": 7},
            "plans_eau":               {"color": "#1a6eb5", "alpha": 0.4, "zorder": 6},
            "routes":                  {"color": "#7A7873", "linewidth": 0.6, "zorder": 5},
            "voies_ferrees":           {"color": "#E24B4A", "linewidth": 1.0, "zorder": 5},
            "vegetation":              {"color": "#1D9E75", "alpha": 0.3, "zorder": 4},
            "batiments":               {"color": "#E8E6E1", "alpha": 0.2, "zorder": 5},
        }

        gdf_perimetre = None
        legend_handles = []

        for nom_couche in carte["couches"]:
            if nom_couche not in couches_gpkg:
                continue
            try:
                gdf = gpd.read_file(str(gpkg), layer=nom_couche)
                if len(gdf) == 0:
                    continue
                gdf_wm = gdf.to_crs("EPSG:3857")

                style = couleurs.get(nom_couche, {"color": "#E8E6E1", "alpha": 0.5})

                if nom_couche == "perimetre_intercommunal":
                    gdf_wm.plot(ax=ax, **style)
                    gdf_perimetre = gdf_wm
                elif nom_couche in ["cours_eau", "voies_ferrees", "routes"]:
                    gdf_wm.plot(ax=ax, **style)
                else:
                    gdf_wm.plot(ax=ax, **style)

                # Légende
                label_map = {
                    "perimetre_intercommunal": territoire["nom"],
                    "communes": "Communes membres",
                    "cours_eau": "Cours d'eau",
                    "plans_eau": "Plans d'eau",
                    "routes": "Routes",
                    "voies_ferrees": "Voies ferrées",
                    "vegetation": "Végétation",
                    "batiments": "Bâtiments",
                }
                if nom_couche in label_map:
                    patch = mpatches.Patch(
                        color=style.get("color", style.get("edgecolor", "#7A7873")),
                        label=label_map[nom_couche],
                        alpha=style.get("alpha", 1.0)
                    )
                    legend_handles.append(patch)

            except Exception:
                continue

        # Fond de carte
        try:
            if fond == "Plan IGN":
                ctx.add_basemap(ax, source=sources_fond["Plan IGN"],
                                crs="EPSG:3857", alpha=0.7, zoom="auto")
            elif fond == "Ortho IGN":
                ctx.add_basemap(ax, source=ctx.providers.GeoportailFrance.orthos,
                                crs="EPSG:3857", alpha=0.6, zoom="auto")
            else:
                ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik,
                                crs="EPSG:3857", alpha=0.5, zoom="auto")
        except Exception:
            pass

        # Zoom sur le territoire
        if gdf_perimetre is not None:
            bounds = gdf_perimetre.total_bounds
            margin = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 0.08
            ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
            ax.set_ylim(bounds[1] - margin, bounds[3] + margin)

        # Suppression des axes
        ax.set_axis_off()

        # ── Habillage cartographique ─────────────────────────
        # Titre
        fig.text(0.12, 0.95, carte["nom"].upper(),
                 fontsize=14, fontweight="bold", color="#E8E6E1",
                 fontfamily="sans-serif", transform=fig.transFigure)
        fig.text(0.12, 0.93, territoire["nom"],
                 fontsize=10, color="#7A7873",
                 fontfamily="sans-serif", transform=fig.transFigure)

        # Source
        fig.text(0.12, 0.02,
                 f"Sources : IGN BD TOPO, Géorisques, SANDRE — Projection : Lambert 93 (EPSG:2154) — MapOS / Sildaro {__import__('datetime').datetime.now().year}",
                 fontsize=7, color="#4A4946",
                 fontfamily="sans-serif", transform=fig.transFigure)

        # Logo MapOS
        fig.text(0.88, 0.02, "MapOS",
                 fontsize=8, color="#E24B4A", fontweight="bold",
                 fontfamily="sans-serif", transform=fig.transFigure, ha="right")

        # Légende
        if legend_handles:
            legend = ax.legend(
                handles=legend_handles,
                loc="lower right",
                framealpha=0.85,
                facecolor="#272724",
                edgecolor="#4A4946",
                labelcolor="#E8E6E1",
                fontsize=8,
            )

        plt.tight_layout(rect=[0, 0.04, 1, 0.92])

        buf = io.BytesIO()
        plt.savefig(buf, format="pdf", dpi=200, facecolor="#1C1C1A",
                    bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    except ImportError as e:
        st.error(f"Module manquant pour la génération PDF : {e}\n"
                 "Installer : pip install matplotlib contextily")
        return None
    except Exception as e:
        st.error(f"Erreur génération carte : {e}")
        return None


def _exporter_toutes(territoire, gpkg, cartes, fmt, orient, fond, nom_safe):
    """Exporte toutes les cartes et propose un ZIP."""
    import zipfile
    import io

    buf_zip = io.BytesIO()
    with zipfile.ZipFile(buf_zip, "w") as zf:
        for carte in cartes:
            if carte["id"] == "atlas":
                continue  # Atlas géré séparément
            with st.spinner(f"{carte['nom']}..."):
                pdf = _generer_carte_pdf(territoire, gpkg, carte, fmt, orient, fond)
                if pdf:
                    zf.writestr(f"{nom_safe}_{carte['id']}.pdf", pdf)

    buf_zip.seek(0)
    st.download_button(
        label="⬇ Télécharger toutes les cartes (.zip)",
        data=buf_zip.read(),
        file_name=f"{nom_safe}_cartes_PICS.zip",
        mime="application/zip",
        use_container_width=True,
    )
