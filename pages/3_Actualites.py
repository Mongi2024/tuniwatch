"""
Page Actualités - Consultation des articles de la base de données
Version 4.2 - Connectée à PostgreSQL + Placeholders Unsplash
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
from db_universal import get_connexion
from placeholder import get_image_or_placeholder

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
# NETTOYAGE HTML
# ============================================================
def nettoyer_html(texte):
    """Nettoie le HTML et décode les entités."""
    if not texte:
        return ""
    texte = str(texte)
    texte = re.sub(r'<[^>]+>', '', texte)
    texte = texte.replace('&#233;', 'é').replace('&#232;', 'è')
    texte = texte.replace('&#224;', 'à').replace('&#226;', 'â')
    texte = texte.replace('&#238;', 'î').replace('&#239;', 'ï')
    texte = texte.replace('&#244;', 'ô').replace('&#251;', 'û')
    texte = texte.replace('&#231;', 'ç').replace('&#235;', 'ë')
    texte = texte.replace('&#8217;', "'").replace('&#8216;', "'")
    texte = texte.replace('&#8220;', '"').replace('&#8221;', '"')
    texte = texte.replace('&#160;', ' ').replace('&#8230;', '...')
    texte = texte.replace('&amp;', '&').replace('&lt;', '<')
    texte = texte.replace('&gt;', '>').replace('&quot;', '"')
    texte = texte.replace('&nbsp;', ' ')
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte


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

        return pd.DataFrame(rows)

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
        curseur.execute("SELECT DISTINCT source FROM articles WHERE source IS NOT NULL AND source != '' ORDER BY source")
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
        curseur.execute("SELECT DISTINCT theme FROM articles WHERE theme IS NOT NULL AND theme != '' AND theme != 'nan' ORDER BY theme")
        return [r[0] for r in curseur.fetchall()]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# FONCTIONS D'AFFICHAGE
# ============================================================
def kpi_card(icone, label, valeur, couleur=C_PRIMAIRE):
    html = (
        f'<div style="background:#ffffff;border-radius:16px;padding:20px 22px;'
        f'box-shadow:0 4px 12px rgba(15,23,42,0.06);border:1px solid rgba(15,23,42,0.04);'
        f'border-left:5px solid {couleur};height:100%;">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
        f'<div style="width:40px;height:40px;background:{couleur}15;border-radius:12px;'
        f'display:flex;align-items:center;justify-content:center;font-size:1.2rem;">{icone}</div>'
        f'<div style="font-size:0.72rem;color:#64748b;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.8px;">{label}</div>'
        f'</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#0f172a;'
        f'line-height:1;letter-spacing:-1px;">{valeur}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_titre(icone, titre, sous_titre=""):
    html = (
        f'<div style="margin:30px 0 16px 0;">'
        f'<h2 style="margin:0;font-size:1.3rem;color:#0f172a;font-weight:800;'
        f'display:flex;align-items:center;gap:12px;">'
        f'<span style="font-size:1.5rem;">{icone}</span>'
        f'<span>{titre}</span>'
        f'</h2>'
    )
    if sous_titre:
        html += f'<p style="margin:6px 0 0 44px;color:#64748b;font-size:0.85rem;">{sous_titre}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def carte_article(row):
    """Affiche une carte d'article avec placeholder si pas d'image."""
    titre = nettoyer_html(row.get("titre", "Sans titre"))[:150]
    source = nettoyer_html(row.get("source", "Inconnue"))[:40]
    date_pub = str(row.get("date_publication", ""))[:10] if row.get("date_publication") else ""
    description = nettoyer_html(row.get("description", ""))
    description = description[:140] + ("..." if len(description) > 140 else "")
    url = str(row.get("url", "#"))
    image_url = row.get("image")
    theme = nettoyer_html(row.get("theme", ""))
    sentiment = row.get("sentiment_cat")

    if sentiment in ("nan", "None", "null", ""):
        sentiment = None
    if theme in ("nan", "None", "null", ""):
        theme = None

    # Récupérer l'image ou le placeholder
    image_finale = get_image_or_placeholder(image_url, theme)

    # Badge de sentiment
    badge_html = ""
    if sentiment and sentiment in ("positif", "negatif", "neutre"):
        colors = {"positif": C_VERT, "negatif": C_ROUGE, "neutre": C_JAUNE}
        color = colors.get(sentiment, "#94a3b8")
        badge_html = (
            f'<span style="display:inline-block;background:{color}20;color:{color};'
            f'padding:2px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;'
            f'text-transform:uppercase;">{sentiment}</span>'
        )

    # Badge de thème
    theme_html = ""
    if theme and theme not in ("nan", "None"):
        theme_html = (
            f'<span style="display:inline-block;background:rgba(139,92,246,0.15);'
            f'color:#8b5cf6;padding:2px 8px;border-radius:12px;font-size:0.65rem;'
            f'font-weight:700;">{theme}</span>'
        )

    # Image (avec placeholder)
    image_html = (
        f'<div style="width:100%;height:160px;border-radius:12px 12px 0 0;'
        f'overflow:hidden;background:#f1f5f9;">'
        f'<img src="{image_finale}" style="width:100%;height:100%;object-fit:cover;" '
        f'onerror="this.src=\'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&h=450&fit=crop\'"/>'
        f'</div>'
    )

    # Description
    desc_html = ""
    if description:
        desc_html = (
            f'<p style="color:#475569;font-size:0.85rem;line-height:1.5;'
            f'margin:8px 0 0 0;">{description}</p>'
        )

    # HTML complet
    html = (
        f'<div style="background:#ffffff;border-radius:12px;overflow:hidden;'
        f'box-shadow:0 2px 8px rgba(15,23,42,0.06);margin-bottom:14px;'
        f'border:1px solid rgba(15,23,42,0.04);">'
        f'{image_html}'
        f'<div style="padding:14px 16px;">'
        f'<div style="font-size:0.7rem;color:{C_PRIMAIRE};font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">'
        f'📰 {source} • {date_pub}</div>'
        f'<a href="{url}" target="_blank" style="color:#0f172a;text-decoration:none;'
        f'font-weight:700;font-size:0.95rem;line-height:1.4;display:block;">{titre}</a>'
        f'{desc_html}'
        f'<div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;">'
        f'{badge_html}{theme_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )
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
    derniere_str = str(derniere)[:16] if derniere else "—"
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