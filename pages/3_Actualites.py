"""
Page Actualites - Recuperation des news en temps reel
avec sauvegarde automatique dans MySQL
Etape C - Session 6
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os


# Ajout du dossier parent au chemin pour importer news_api et db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from news_api import recuperer_news, recuperer_news_multi, est_configure

import auth
import style
style.appliquer_style()
# Configuration de la page
st.set_page_config(
    page_title="Actualites - Monitoring",
    page_icon="📰",
    layout="wide"
)

# Protection
auth.require_login()
# ============================================================
# VERIFICATION DE LA CONFIGURATION
# ============================================================
if not est_configure():
    st.error("⚠️ Clé API NewsAPI non configurée.")
    st.info("Ajoutez votre clé dans le fichier `.env` : `NEWSAPI_KEY=votre_cle`")
    st.stop()

# ============================================================
# FILTRES DANS LA SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📰 Filtres Actualités")

    # Mots-cles predefinis
    sujets_predefinis = [
        "Tunisie",
        "intelligence artificielle",
        "python",
        "cybersecurite",
        "reseaux sociaux",
        "innovation",
        "economie",
        "sport"
    ]

    # Ou mots-cles personnalises
    sujet_perso = st.text_input(
        "🔍 Sujet personnalisé",
        placeholder="Ex: climat",
        key="news_sujet"
    )

    if not sujet_perso:
        sujet_choisi = st.selectbox(
            "📌 Ou choisir un sujet",
            sujets_predefinis,
            key="news_sujet_predef"
        )
        mots_cles = [sujet_choisi]
    else:
        mots_cles = [s.strip() for s in sujet_perso.split(",") if s.strip()]

    # Nombre d'articles
    nb_articles = st.slider(
        "📊 Nombre d'articles",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
        key="news_nb"
    )

    # Periode
    jours = st.selectbox(
        "📅 Sur les X derniers jours",
        [1, 3, 7, 14, 30],
        index=2,
        key="news_jours"
    )

    # Bouton de recuperation
    if st.button("🔄 Récupérer les news", use_container_width=True, key="news_bouton"):
        st.session_state["news_recuperees"] = True
        # Vider le cache pour forcer le rechargement depuis l'API
        st.cache_data.clear()

# ============================================================
# TITRE + COMPTEUR MYSQL
# ============================================================
st.title("📰 Actualités en temps réel")
st.caption("Articles récupérés via NewsAPI — Sources internationales")

# ============================================================
# COMPTEUR D'ARTICLES EN BASE MYSQL
# ============================================================
try:
    import db
    nb_total = db.compter_articles()

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("📚 Articles en base MySQL", nb_total)
    col_stat2.metric("🔍 Critère actuel", ", ".join(mots_cles)[:25])
    col_stat3.metric("📅 Période", f"{jours} jours")

    st.markdown("---")
except Exception as e:
    st.warning(f"⚠️ MySQL non accessible : {e}")
    st.markdown("---")

# ============================================================
# RECUPERATION DES NEWS
# ============================================================

# Cache pour eviter de re-appeler l'API a chaque interaction
@st.cache_data(ttl=300)  # Cache de 5 minutes
def charger_news(mots_cles_tuple, nb, jours):
    """Recupere les news et les sauvegarde dans MySQL."""
    articles = recuperer_news_multi(list(mots_cles_tuple), nb_par_mot=nb, jours=jours)

    # Sauvegarde automatique dans MySQL
    if articles:
        try:
            import db
            db.sauvegarder_articles(articles)
        except Exception as e:
            print(f"Erreur sauvegarde MySQL : {e}")

    return articles

# Boutons de contrôle
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    recharger = st.button("🔄 Recharger", use_container_width=True, key="news_reload")

with col_btn2:
    vider_cache = st.button("🗑️ Vider le cache", use_container_width=True, key="news_clear")

if vider_cache:
    charger_news.clear()

# Chargement des news
with st.spinner("⏳ Récupération des articles..."):
    if recharger:
        charger_news.clear()

    articles = charger_news(tuple(mots_cles), nb_articles, jours)

# ============================================================
# AFFICHAGE DES RESULTATS
# ============================================================

if not articles:
    st.warning("Aucun article trouvé pour ces critères.")
    st.info("💡 Essayez avec un autre mot-clé ou augmentez la période.")
else:
    df = pd.DataFrame(articles)

    # --- KPIs ---
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📰 Articles", len(df))
    col2.metric("🌐 Sources uniques", df["source"].nunique())
    col3.metric("🔑 Mots-clés", len(mots_cles))

    # Nombre de sources actives
    source_principale = df["source"].value_counts().index[0] if len(df) > 0 else "—"
    col4.metric("🏆 Top source", source_principale[:20])

    st.markdown("---")

    # --- Filtres dans la page ---
    st.subheader("🎛️ Filtrer les résultats")

    col_a, col_b = st.columns(2)

    with col_a:
        sources_dispo = ["Toutes"] + sorted(df["source"].unique().tolist())
        source_filtre = st.selectbox("Source", sources_dispo, key="news_source_filter")

    with col_b:
        recherche_titre = st.text_input(
            "Recherche dans les titres",
            placeholder="Ex: Trump, Google...",
            key="news_titre_filter"
        )

    # Application des filtres
    df_filtre = df.copy()
    if source_filtre != "Toutes":
        df_filtre = df_filtre[df_filtre["source"] == source_filtre]
    if recherche_titre:
        df_filtre = df_filtre[
            df_filtre["titre"].str.contains(recherche_titre, case=False, na=False)
        ]

    st.caption(f"**{len(df_filtre)}** article(s) affiché(s) après filtrage")

    # --- Liste des articles ---
    st.markdown("---")
    st.subheader("📄 Articles")

    for i, article in df_filtre.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 4])

            with col1:
                if article["image"]:
                    try:
                        st.image(article["image"], use_container_width=True)
                    except Exception:
                        st.write("🖼️")
                else:
                    st.write("🖼️")

            with col2:
                st.markdown(f"### [{article['titre']}]({article['url']})")
                st.caption(
                    f"**{article['source']}** • "
                    f"{article['date'][:10]} • "
                    f"{article.get('mot_cle', '')}"
                )
                if article["description"]:
                    st.write(article["description"][:200] + "...")

            st.markdown("---")

    # --- Export CSV ---
    st.subheader("📥 Exporter les résultats")
    csv = df_filtre.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv,
        file_name=f"news_{mots_cles[0].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption(f"Page Actualités — Version 0.2 (MySQL) | Dernière MAJ : {datetime.now().strftime('%H:%M:%S')}")
style.footer()