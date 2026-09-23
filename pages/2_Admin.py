"""
Page Admin - Gestion des sources et paramètres
Version 2.0 - Connectée à PostgreSQL
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
from db_universal import get_connexion

style.appliquer_style()

st.set_page_config(
    page_title="Admin - TuniWatch",
    page_icon="⚙️",
    layout="wide"
)

auth.require_super_admin()

# ============================================================
# TITRE
# ============================================================
st.title("⚙️ Espace Administrateur")
st.caption("Gestion des sources, statistiques système et paramètres")
st.markdown("---")


# ============================================================
# FONCTIONS
# ============================================================
@st.cache_data(ttl=60)
def stats_systeme():
    """Récupère les statistiques système."""
    conn = get_connexion()
    if conn is None:
        return {}
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM articles) AS total_articles,
                (SELECT COUNT(*) FROM sources) AS total_sources,
                (SELECT COUNT(*) FROM mots_cles WHERE actif = 1) AS total_mots_cles,
                (SELECT COUNT(*) FROM utilisateurs) AS total_utilisateurs,
                (SELECT COUNT(*) FROM alertes) AS total_alertes,
                (SELECT COUNT(*) FROM alertes WHERE lue = 0) AS alertes_non_lues,
                (SELECT MAX(date_ajout) FROM articles) AS derniere_collecte,
                (SELECT AVG(score) FROM articles_sentiment) AS score_moyen
        """)
        result = curseur.fetchone()
        return {
            "total_articles": int(result.get("total_articles") or 0),
            "total_sources": int(result.get("total_sources") or 0),
            "total_mots_cles": int(result.get("total_mots_cles") or 0),
            "total_utilisateurs": int(result.get("total_utilisateurs") or 0),
            "total_alertes": int(result.get("total_alertes") or 0),
            "alertes_non_lues": int(result.get("alertes_non_lues") or 0),
            "derniere_collecte": str(result.get("derniere_collecte"))[:16] if result.get("derniere_collecte") else "—",
            "score_moyen": round(float(result.get("score_moyen") or 0), 2)
        } if result else {}
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=60)
def liste_sources_db():
    """Liste les sources depuis la table sources."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, nom, url_rss, actif
            FROM sources
            ORDER BY nom
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=60)
def sources_articles():
    """Liste les sources distinctes des articles avec leur nombre."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT source AS nom, COUNT(*) AS nb_articles
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=60)
def repartition_themes():
    """Répartition des articles par thème."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT theme, COUNT(DISTINCT article_id) AS nb
            FROM articles_themes
            GROUP BY theme
            ORDER BY nb DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# SECTION 1 : STATISTIQUES SYSTÈME
# ============================================================
st.subheader("📊 Statistiques système")

with st.spinner("Chargement..."):
    stats = stats_systeme()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📰 Articles", f"{stats.get('total_articles', 0):,}".replace(",", " "))

with col2:
    st.metric("📡 Sources", stats.get('total_sources', 0))

with col3:
    st.metric("🔑 Mots-clés actifs", stats.get('total_mots_cles', 0))

with col4:
    st.metric("👥 Utilisateurs", stats.get('total_utilisateurs', 0))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🚨 Alertes totales", stats.get('total_alertes', 0))

with col2:
    st.metric("🔔 Alertes non lues", stats.get('alertes_non_lues', 0))

with col3:
    st.metric("⭐ Score moyen", stats.get('score_moyen', 0))

with col4:
    st.metric("🕐 Dernière collecte", stats.get('derniere_collecte', '—'))

st.markdown("---")

# ============================================================
# SECTION 2 : SOURCES SUIVIES (depuis la base)
# ============================================================
st.subheader("🌐 Sources suivies (avec articles collectés)")

with st.spinner("Chargement des sources..."):
    sources_data = sources_articles()

if not sources_data:
    st.warning("Aucune source avec articles pour le moment.")
else:
    st.caption(f"**{len(sources_data)}** sources actives dans la base")

    for src in sources_data[:20]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📡 **{src['nom']}**")
        with col2:
            st.write(f"{src['nb_articles']} articles")
        st.markdown("")

    if len(sources_data) > 20:
        st.info(f"… et {len(sources_data) - 20} autres sources")

st.markdown("---")

# ============================================================
# SECTION 3 : RÉPARTITION PAR THÈME
# ============================================================
st.subheader("🎯 Répartition par thème")

with st.spinner("Chargement des thèmes..."):
    themes_data = repartition_themes()

if not themes_data:
    st.warning("Aucun thème détecté.")
else:
    for th in themes_data:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"🎯 **{th['theme']}**")
        with col2:
            st.write(f"{th['nb']} articles")
        st.markdown("")

st.markdown("---")

# ============================================================
# SECTION 4 : PARAMÈTRES DES ALERTES
# ============================================================
st.subheader("🚨 Paramètres des alertes (informatif)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **📌 Seuils de détection (dans `alert_detector.py`)**

    - **Sentiment négatif** : score < -0.5 sur ≥ 2 articles
    - **Pic de mentions** : x2 sur 3 jours (min 5 articles)
    - **Baisse d'activité** : -50% (min 5 articles)
    - **Pic global** : x3 en 1 jour (min 20 articles)
    """)

with col2:
    st.markdown("""
    **⚙️ Automatisation**

    - **Cron** : Analyse toutes les 2h (`crontab -e`)
    - **Fichier** : `/root/tuniwatch/analysis.log`
    - **Commande** : `python3 /root/tuniwatch/run_analysis.py`
    """)

st.markdown("---")

# ============================================================
# SECTION 5 : ACTIONS
# ============================================================
st.subheader("🛠️ Actions système")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Rafraîchir les données", use_container_width=True, key="admin_refresh"):
        st.cache_data.clear()
        st.success("Cache vidé et données rafraîchies !")
        st.rerun()

with col2:
    if st.button("📊 Voir les logs", use_container_width=True, key="admin_logs"):
        st.info("Logs disponibles sur le VPS : `/root/tuniwatch/analysis.log`")

with col3:
    if st.button("🗑️ Vider le cache", use_container_width=True, key="admin_clear_cache"):
        st.cache_data.clear()
        st.success("Cache vidé !")
        st.rerun()

st.markdown("---")
st.caption("Page Admin — Version 2.0")
style.footer()