"""
Page Actualités - Consultation des articles de la base de données
Version 4.0 - Connectée à PostgreSQL (n8n)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import cockpit_stats
from db_universal import get_connexion

st.set_page_config(
    page_title="Actualités - TuniWatch",
    page_icon="📰",
    layout="wide"
)

style.appliquer_style()
auth.require_login()

# ============================================================
# PALETTE
# ============================================================
C_PRIMAIRE = "#e70013"
C_TEAL = "#14b8a6"
C_JAUNE = "#f59e0b"
C_VIOLET = "#8b5cf6"
C_VERT = "#10b981"
C_ROUGE = "#ef4444"


# ============================================================
# FONCTIONS DE CHARGEMENT
# ============================================================
@st.cache_data(ttl=120)
def charger_articles(limite=100, source=None, theme=None, sentiment=None, recherche=None, jours=None):
    """Charge les articles depuis PostgreSQL avec filtres."""
    conn = get_connexion()
    if conn is None:
        return pd.DataFrame()

    curseur = conn.cursor(dictionary=True)
    try:
        requete = """
            SELECT 
                a.id,
                a.titre,
                a.source,
                a.auteur,
                a.date_publication,
                a.date_ajout,
                a.url,
                a.description,
                a.image,
                a.sentiment,
                a.theme,
                a.mot_cle,
                s.sentiment AS sentiment_cat,
                s.score AS sentiment_score
            FROM articles a
            LEFT JOIN articles_sentiment s ON s.article_id = a.id
            WHERE 1=1
        """
        params = []

        if source and source != "Toutes":
            requete += " AND a.source = %s"
            params.append(source)

        if theme and theme != "Tous":
            requete += " AND a.theme = %s"
            params.append(theme)

        if sentiment and sentiment != "Tous":
            requete += " AND s.sentiment = %s"
            params.append(sentiment)

        if recherche:
            requete += " AND (a.titre ILIKE %s OR a.description ILIKE %s)"
            params.append(f"%{recherche}%")
            params.append(f"%{recherche}%")

        if jours:
            requete += " AND a.date_ajout >= NOW() - INTERVAL '%s days'"
            params.append(jours)

        requete += " ORDER BY a.date_ajout DESC LIMIT %s"
        params.append(limite)

        curseur.execute(requete, params)
        rows = curseur.fetchall()

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        st.error(f"Erreur chargement : {e}")
        return pd.DataFrame()
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=300)
def charger_stats():
    """Charge les stats globales."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                COUNT(*) AS total,
                COUNT(DISTINCT source) AS nb_sources,
                COUNT(DISTINCT theme) AS nb_themes,
                MAX(date_ajout) AS derniere_collecte
            FROM articles
        """)
        return curseur.fetchone() or {}
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=300)
def charger_sources():
    """Liste les sources uniques."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor()
    try:
        curseur.execute("SELECT DISTINCT source FROM articles WHERE source IS NOT NULL ORDER BY source")
        return [r[0] for r in curseur.fetchall()]
    finally:
        curseur.close()
        conn.close()


@st.cache_data(ttl=300)
def charger_themes():
    """Liste les thèmes uniques."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor()
    try:
        curseur.execute("SELECT DISTINCT theme FROM articles WHERE theme IS NOT NULL AND theme != '' ORDER BY theme")
        return [r[0] for r in curseur.fetchall()]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# FONCTIONS D'AFFICHAGE
# ============================================================
def kpi_card(icone, label, valeur, couleur=C_PRIMAIRE):
    html = f'''
    <div style="
        background: #ffffff;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(15, 23, 42, 0.04);
        border-left: 5px solid {couleur};
        height: 100%;
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="
                width: 40px; height: 40px;
                background: {couleur}15;
                border-radius: 12px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.2rem;
            ">{icone}</div>
            <div style="
                font-size: 0.72rem; color: #64748b; font-weight: 700;
                text-transform: uppercase; letter-spacing: 0.8px;
            ">{label}</div>
        </div>
        <div style="
            font-size: 2rem; font-weight: 800; color: #0f172a;
            line-height: 1; letter-spacing: -1px;
        ">{valeur}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def section_titre(icone, titre, sous_titre=""):
    html = f'''
    <div style="margin: 30px 0 16px 0;">
        <h2 style="
            margin: 0; font-size: 1.3rem; color: #0f172a;
            font-weight: 800; display: flex; align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.5rem;">{icone}</span>
            <span>{titre}</span>
        </h2>
        {f'<p style="margin: 6px 0 0 44px; color: #64748b; font-size: 0.85rem;">{sous_titre}</p>' if sous_titre else ''}
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def carte_article(row):
    """Affiche une carte d'article."""
    titre = str(row.get("titre", "Sans titre"))[:150]
    source = row.get("source", "Inconnue")
    date_pub = str(row.get("date_publication", ""))[:10] if row.get("date_publication") else ""
    description = str(row.get("description", ""))[:200] if row.get("description") else ""
    url = row.get("url", "#")
    image_url = row.get("image")
    theme = row.get("theme", "")
    sentiment = row.get("sentiment_cat")

    # Badge de sentiment
    badge_html = ""
    if sentiment:
        colors = {"positif": C_VERT, "negatif": C_ROUGE, "neutre": C_JAUNE}
        color = colors.get(sentiment, "#94a3b8")
        badge_html = f'''
        <span style="
            display: inline-block;
            background: {color}20;
            color: {color};
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
        ">{sentiment}</span>
        '''

    # Badge de thème
    theme_html = ""
    if theme:
        theme_html = f'''
        <span style="
            display: inline-block;
            background: rgba(139, 92, 246, 0.15);
            color: #8b5cf6;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 700;
        ">{theme}</span>
        '''

    # Image
    if image_url:
        image_html = f'''
        <div style="width: 100%; height: 160px; border-radius: 12px 12px 0 0; overflow: hidden; background: #f1f5f9;">
            <img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;"
                 onerror="this.style.display='none'"/>
        </div>
        '''
    else:
        image_html = f'''
        <div style="width: 100%; height: 100px; border-radius: 12px 12px 0 0;
             background: linear-gradient(135deg, {C_PRIMAIRE} 0%, #b8000f 100%);
             display: flex; align-items: center; justify-content: center;
             color: white; font-size: 2rem;">📰</div>
        '''

    # Description
    desc_html = f'<p style="color: #475569; font-size: 0.85rem; line-height: 1.5; margin: 8px 0 0 0;">{description}...</p>' if description else ''

    html = f'''
    <div style="
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        margin-bottom: 14px;
        border: 1px solid rgba(15, 23, 42, 0.04);
    ">
        {image_html}
        <div style="padding: 14px 16px;">
            <div style="font-size: 0.7rem; color: {C_PRIMAIRE}; font-weight: 700;
                 text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                📰 {source} • {date_pub}
            </div>
            <a href="{url}" target="_blank" style="
                color: #0f172a; text-decoration: none;
                font-weight: 700; font-size: 0.95rem;
                line-height: 1.4; display: block;
            ">{titre}</a>
            {desc_html}
            <div style="margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap;">
                {badge_html}
                {theme_html}
            </div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# EN-TÊTE
# ============================================================
style.page_header(
    titre="Actualités",
    icone="📰",
    description="Tous les articles collectés automatiquement par n8n — Filtres par source, thème et sentiment",
    badge="BASE DE DONNÉES"
)

# ============================================================
# CHARGEMENT DES FILTRES
# ============================================================
with st.spinner("Chargement des filtres..."):
    stats = charger_stats()
    sources_liste = ["Toutes"] + charger_sources()
    themes_liste = ["Tous"] + charger_themes()

# ============================================================
# KPI GLOBAUX
# ============================================================
section_titre("📊", "Vue d'ensemble", "Statistiques de la base de données")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("📰", "Articles", f"{stats.get('total', 0):,}".replace(",", " "), C_PRIMAIRE)

with col2:
    kpi_card("📡", "Sources", stats.get("nb_sources", 0), C_TEAL)

with col3:
    kpi_card("🎯", "Thèmes", stats.get("nb_themes", 0), C_JAUNE)

with col4:
    derniere = stats.get("derniere_collecte")
    if derniere:
        derniere_str = str(derniere)[:16]
    else:
        derniere_str = "—"
    kpi_card("🕐", "Dernière collecte", derniere_str, C_VIOLET)

# ============================================================
# FILTRES
# ============================================================
section_titre("🎛️", "Filtres", "Affinez votre recherche")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    recherche = st.text_input(
        "🔍 Rechercher dans les titres et descriptions",
        placeholder="Ex: Tunisie, météo, économie...",
        key="actu_recherche"
    )

with col2:
    source_filtre = st.selectbox("📡 Source", sources_liste, key="actu_source")

with col3:
    theme_filtre = st.selectbox("🎯 Thème", themes_liste, key="actu_theme")

with col4:
    sentiment_filtre = st.selectbox(
        "😊 Sentiment",
        ["Tous", "positif", "neutre", "negatif"],
        key="actu_sentiment"
    )

# Slider pour la limite
col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    limite = st.slider("📊 Nombre d'articles", 10, 500, 50, 10, key="actu_limite")
with col_b:
    jours = st.selectbox("📅 Période", [None, 1, 3, 7, 14, 30, 90], index=6,
                          format_func=lambda x: "Toutes" if x is None else f"{x} jours",
                          key="actu_jours")

# ============================================================
# CHARGEMENT DES ARTICLES
# ============================================================
with st.spinner("Chargement des articles..."):
    df = charger_articles(
        limite=limite,
        source=source_filtre if source_filtre != "Toutes" else None,
        theme=theme_filtre if theme_filtre != "Tous" else None,
        sentiment=sentiment_filtre if sentiment_filtre != "Tous" else None,
        recherche=recherche if recherche else None,
        jours=jours
    )

# ============================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================
if df.empty:
    st.warning("Aucun article ne correspond aux critères.")
    st.info("💡 Essayez d'élargir la période ou de retirer des filtres.")
else:
    st.caption(f"**{len(df)}** article(s) affiché(s)")

    section_titre("📄", "Articles", "Cliquez sur un titre pour ouvrir l'article")

    # Affichage en 3 colonnes
    nb_cols = 3
    cols = st.columns(nb_cols, gap="medium")

    for i, (_, row) in enumerate(df.iterrows()):
        col = cols[i % nb_cols]
        with col:
            carte_article(row)

    # Export CSV
    section_titre("📥", "Exporter", "Télécharger la liste filtrée")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv,
        file_name=f"actualites_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# ============================================================
# FOOTER
# ============================================================
style.footer()