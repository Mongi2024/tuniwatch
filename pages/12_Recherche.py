"""
Page Recherche - Recherche avancee dans les articles
Etape J - Polish final
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import favicon_config
import mysql.connector
from mysql.connector import Error

# Configuration
favicon_config.setup_page("Recherche", "🔍", "wide")

# Style
style.appliquer_style()

# Protection
auth.require_login()


# ============================================================
# FONCTION RECHERCHE
# ============================================================
def rechercher_articles(
    texte=None,
    source=None,
    theme=None,
    sentiment=None,
    langue=None,
    jours=None,
    limite=100
):
    """Recherche avancee dans les articles."""
    try:
        conn = mysql.connector.connect(**{
            "host": "localhost", "port": 3306,
            "user": "python_user", "password": "PythonUser2026!",
            "database": "monitoring", "charset": "utf8mb4"
        })
    except Error:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        requete = """
            SELECT DISTINCT
                a.id, a.titre, a.source, a.url, a.date_publication, a.date_ajout,
                at.theme, at.score AS score_theme,
                s.sentiment, s.score AS score_sentiment, s.langue_detectee
            FROM articles a
            LEFT JOIN articles_themes at ON at.article_id = a.id
            LEFT JOIN articles_sentiment s ON s.article_id = a.id
            WHERE 1=1
        """
        params = []

        if texte:
            requete += " AND (a.titre LIKE %s OR a.description LIKE %s)"
            params.extend([f"%{texte}%", f"%{texte}%"])

        if source and source != "Toutes":
            requete += " AND a.source = %s"
            params.append(source)

        if theme and theme != "Tous":
            requete += " AND at.theme = %s"
            params.append(theme)

        if sentiment and sentiment != "Tous":
            requete += " AND s.sentiment = %s"
            params.append(sentiment)

        if langue and langue != "Toutes":
            requete += " AND s.langue_detectee = %s"
            params.append(langue)

        if jours:
            requete += " AND a.date_ajout >= DATE_SUB(NOW(), INTERVAL %s DAY)"
            params.append(jours)

        requete += " ORDER BY a.date_ajout DESC LIMIT %s"
        params.append(limite)

        curseur.execute(requete, params)
        return curseur.fetchall()
    except Error as e:
        st.error(f"Erreur recherche : {e}")
        return []
    finally:
        curseur.close()
        conn.close()


def lister_sources():
    try:
        conn = mysql.connector.connect(**{
            "host": "localhost", "port": 3306,
            "user": "python_user", "password": "PythonUser2026!",
            "database": "monitoring", "charset": "utf8mb4"
        })
        curseur = conn.cursor()
        curseur.execute("""
            SELECT DISTINCT source FROM articles
            WHERE source IS NOT NULL AND source != ''
            ORDER BY source
        """)
        result = [r[0] for r in curseur.fetchall()]
        curseur.close()
        conn.close()
        return result
    except Error:
        return []


# ============================================================
# EN-TETE
# ============================================================
style.page_header(
    "Recherche avancée",
    "🔍",
    "Explorez les 400+ articles collectés avec des filtres puissants"
)

# ============================================================
# BARRE DE RECHERCHE
# ============================================================
col1, col2 = st.columns([3, 1])

with col1:
    texte = st.text_input(
        "🔎 Rechercher dans les titres et descriptions",
        placeholder="Ex: Tunisie, gouvernement, santé, تعليم...",
        key="search_texte"
    )

with col2:
    limite = st.selectbox(
        "Résultats max",
        [50, 100, 200, 500],
        index=1,
        key="search_limite"
    )

# ============================================================
# FILTRES AVANCES
# ============================================================
with st.expander("🎛️ Filtres avancés", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        sources_dispo = ["Toutes"] + lister_sources()
        source_filtre = st.selectbox("📡 Source", sources_dispo, key="search_source")

        theme_filtre = st.selectbox(
            "🎯 Thème",
            ["Tous", "violence_femmes", "discours_haine", "presence_femmes",
             "presence_handicapes", "presence_jeunes", "equilibre_politique",
             "equilibre_regional"],
            key="search_theme"
        )

    with col2:
        sentiment_filtre = st.selectbox(
            "😊 Sentiment",
            ["Tous", "positif", "neutre", "negatif"],
            key="search_sentiment"
        )

        langue_filtre = st.selectbox(
            "🌍 Langue",
            ["Toutes", "fr", "ar", "inconnu"],
            key="search_langue"
        )

    with col3:
        periode = st.selectbox(
            "📅 Période",
            ["Tout", "7 derniers jours", "30 derniers jours", "90 derniers jours"],
            key="search_periode"
        )

        jours_map = {
            "Tout": None,
            "7 derniers jours": 7,
            "30 derniers jours": 30,
            "90 derniers jours": 90
        }
        jours_filtre = jours_map.get(periode)

# ============================================================
# RECHERCHE
# ============================================================
with st.spinner("Recherche en cours..."):
    resultats = rechercher_articles(
        texte=texte if texte else None,
        source=source_filtre,
        theme=theme_filtre,
        sentiment=sentiment_filtre,
        langue=langue_filtre,
        jours=jours_filtre,
        limite=limite
    )

# ============================================================
# AFFICHAGE DES RESULTATS
# ============================================================
st.markdown("---")

if not resultats:
    st.info("💡 Aucun résultat. Essayez d'élargir vos critères de recherche.")
else:
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)

    sources_uniques = len(set(r["source"] for r in resultats if r["source"]))
    themes_uniques = len(set(r["theme"] for r in resultats if r["theme"]))
    sentiments_count = {}
    for r in resultats:
        s = r.get("sentiment") or "non analysé"
        sentiments_count[s] = sentiments_count.get(s, 0) + 1

    col1.metric("📰 Résultats", len(resultats))
    col2.metric("📡 Sources", sources_uniques)
    col3.metric("🎯 Thèmes", themes_uniques)
    col4.metric(
        "😊 Sentiment dominant",
        max(sentiments_count.items(), key=lambda x: x[1])[0] if sentiments_count else "—"
    )

    st.markdown("---")

    # Liste des résultats
    st.subheader(f"📋 {len(resultats)} article(s) trouvé(s)")

    for i, art in enumerate(resultats, 1):
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                # Titre cliquable
                titre = art.get("titre", "Sans titre")
                url = art.get("url", "")
                if url:
                    st.markdown(f"**{i}. [{titre[:150]}]({url})**")
                else:
                    st.markdown(f"**{i}. {titre[:150]}**")

                # Meta
                meta = []
                if art.get("source"):
                    meta.append(f"📰 {art['source']}")

                if art.get("date_publication"):
                    date_str = str(art["date_publication"])[:10]
                    meta.append(f"📅 {date_str}")

                if art.get("theme"):
                    emoji = {
                        "violence_femmes": "⚖️", "discours_haine": "🚨",
                        "presence_femmes": "👩", "presence_handicapes": "👥",
                        "presence_jeunes": "🧑", "equilibre_politique": "🏛️",
                        "equilibre_regional": "🗺️"
                    }.get(art["theme"], "🌐")
                    meta.append(f"{emoji} {art['theme']} ({art['score_theme']:.1f})")

                st.caption(" • ".join(meta))

            with col2:
                # Badge sentiment
                sentiment = art.get("sentiment")
                if sentiment:
                    emoji_s = {"positif": "🟢", "neutre": "🟡", "negatif": "🔴"}.get(sentiment, "⚪")
                    st.markdown(f"""
                    <div style="text-align: center; padding: 8px;
                                background: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 1.5rem;">{emoji_s}</div>
                        <div style="font-size: 0.7rem; color: #666;">{sentiment}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("")

    # Export CSV
    st.markdown("---")
    df_export = pd.DataFrame(resultats)
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Exporter les résultats en CSV",
        data=csv,
        file_name=f"recherche_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

st.markdown("---")
style.footer()