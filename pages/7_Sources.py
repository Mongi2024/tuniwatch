"""
Page Sources - Gestion des sources de collecte
Etape B - Session 2
Reserve aux administrateurs
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import collector_ui
import rss_collector
import style
style.appliquer_style()
# Configuration
st.set_page_config(
    page_title="Sources - Monitoring",
    page_icon="📡",
    layout="wide"
)

# Protection ADMIN
auth.require_admin()

# ============================================================
# TITRE
# ============================================================
st.title("📡 Sources de collecte")
st.caption("Gestion des médias et réseaux sociaux tunisiens")

st.markdown("---")

# ============================================================
# STATISTIQUES
# ============================================================
st.subheader("📊 Statistiques globales")

stats_cat = collector_ui.stats_sources()
total_sources = sum(stats_cat.values())
avec_rss = collector_ui.compter_avec_rss()

col1, col2, col3, col4 = st.columns(4)

col1.metric("📡 Total sources", total_sources)
col2.metric("🔗 Avec flux RSS", avec_rss)
col3.metric("📰 Presse", stats_cat.get("presse", 0))
col4.metric("📻 Radios", stats_cat.get("radio", 0))

st.markdown("---")

# ============================================================
# BOUTON COLLECTE GLOBALE
# ============================================================
st.subheader("🚀 Lancer la collecte")

col_a, col_b = st.columns([1, 3])

with col_a:
    if st.button("🔄 Collecter TOUT", type="primary", use_container_width=True, key="btn_collect_all"):
        with st.spinner("Collecte en cours... cela peut prendre 1-2 minutes"):
            try:
                resultat = rss_collector.collecter_tout(max_par_source=30)
                st.success(f"✅ Collecte terminée : {resultat['articles']} articles ajoutés")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

with col_b:
    st.info(
        "💡 **Collecter TOUT** : lance la collecte sur toutes les sources RSS actives "
        "(presse + radios). Prend ~1-2 minutes."
    )

st.markdown("---")

# ============================================================
# FILTRES
# ============================================================
st.subheader("📋 Liste des sources")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    categories_dispo = ["Toutes"] + sorted(stats_cat.keys())
    categorie_filtre = st.selectbox(
        "Filtrer par catégorie",
        categories_dispo,
        key="sources_cat_filter"
    )

with col2:
    afficher_inactives = st.checkbox(
        "Afficher les inactives",
        value=False,
        key="sources_show_inactive"
    )

with col3:
    recherche = st.text_input(
        "🔍 Rechercher une source",
        placeholder="Ex: Radio, La Presse...",
        key="sources_search"
    )

st.markdown("---")

# ============================================================
# CHARGEMENT DES SOURCES
# ============================================================
cat = None if categorie_filtre == "Toutes" else categorie_filtre
sources = collector_ui.lister_sources(
    categorie=cat,
    actives_seulement=not afficher_inactives
)

# Filtrer par recherche
if recherche:
    sources = [s for s in sources if recherche.lower() in s["nom"].lower()]

# Stats articles par source
stats_articles = {s["source"]: s["nb_articles"] for s in collector_ui.stats_articles_par_source()}

st.caption(f"**{len(sources)}** source(s) affichée(s)")

# ============================================================
# AFFICHAGE DES SOURCES
# ============================================================
if not sources:
    st.warning("Aucune source trouvée.")
else:
    for src in sources:
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1.2, 1, 1])

            with col1:
                emoji_cat = {
                    "presse": "📰",
                    "radio": "📻",
                    "tv": "📺",
                    "facebook": "📘",
                    "twitter": "🐦",
                    "youtube": "📹",
                    "tiktok": "🎵"
                }.get(src["categorie"], "🌐")

                st.markdown(f"{emoji_cat} **{src['nom']}**")

            with col2:
                st.caption(f"🌍 {src['langue']}")

            with col3:
                if src["url_rss"]:
                    st.write("✅ RSS")
                else:
                    st.write("❌ RSS")

            with col4:
                nb_articles = stats_articles.get(src["nom"], 0)
                st.metric("Articles", nb_articles, label_visibility="collapsed")
                st.caption(f"📰 {nb_articles} art.")

            with col5:
                if src["actif"]:
                    if st.button("❌ Désactiver", key=f"toggle_{src['id']}", use_container_width=True):
                        ok, msg = collector_ui.basculer_actif(src["id"], True)
                        if ok:
                            st.success(msg)
                            st.rerun()
                else:
                    if st.button("✅ Activer", key=f"toggle_{src['id']}", use_container_width=True):
                        ok, msg = collector_ui.basculer_actif(src["id"], False)
                        if ok:
                            st.success(msg)
                            st.rerun()

            with col6:
                if st.button("🗑️", key=f"del_{src['id']}", help="Supprimer", use_container_width=True):
                    ok, msg = collector_ui.supprimer_source(src["id"], src["nom"])
                    if ok:
                        st.success(msg)
                        st.rerun()

            # Details expandable
            with st.expander(f"🔍 Détails : {src['nom']}"):
                colA, colB = st.columns(2)
                colA.write(f"**ID** : {src['id']}")
                colA.write(f"**Catégorie** : {src['categorie']}")
                colA.write(f"**Langue** : {src['langue']}")
                colA.write(f"**Actif** : {'✅' if src['actif'] else '❌'}")

                colB.write(f"**Site** : {src['url_site'] or 'Non renseigné'}")
                colB.write(f"**Flux RSS** : {src['url_rss'] or 'Non renseigné'}")
                colB.write(f"**Ajoutée le** : {src['date_ajout']}")

            st.markdown("---")

# ============================================================
# AJOUTER UNE SOURCE
# ============================================================
st.subheader("➕ Ajouter une nouvelle source")

with st.form("form_add_source"):
    col1, col2 = st.columns(2)

    with col1:
        new_nom = st.text_input(
            "📝 Nom de la source",
            placeholder="Ex: Radio Kairouan",
            key="new_source_nom"
        )

        new_categorie = st.selectbox(
            "🏷️ Catégorie",
            ["presse", "radio", "tv", "facebook", "twitter", "youtube", "tiktok"],
            key="new_source_cat"
        )

    with col2:
        new_langue = st.selectbox(
            "🌍 Langue principale",
            ["fr", "ar", "ar_tn", "arabizi", "mixed"],
            key="new_source_langue"
        )

        new_url_site = st.text_input(
            "🔗 URL du site",
            placeholder="https://...",
            key="new_source_site"
        )

    new_url_rss = st.text_input(
        "📡 URL du flux RSS (optionnel)",
        placeholder="https://.../rss ou /feed",
        key="new_source_rss"
    )

    submit = st.form_submit_button(
        "Ajouter la source",
        use_container_width=True,
        type="primary"
    )

    if submit:
        if not new_nom:
            st.error("⚠️ Le nom est obligatoire.")
        else:
            ok, msg = collector_ui.ajouter_source(
                new_nom, new_categorie, new_langue,
                new_url_site, new_url_rss
            )
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

st.markdown("---")
st.caption(f"Page Sources — Version 0.1 | Dernière MAJ : {datetime.now().strftime('%H:%M:%S')}")
style.footer()