"""
Page Actualités - Récupération des news en temps réel
Version 3.0 - Filtres médias + sujets + recherche rapide
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from news_api import recuperer_news_multi, est_configure

import auth
import style
import cockpit_stats

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
C_BLEU = "#3b82f6"
C_VERT = "#10b981"
C_ROUGE = "#ef4444"

# ============================================================
# SUJETS PRÉDÉFINIS
# ============================================================
SUJETS_PREDEFINIS = [
    "Tunisie",
    "intelligence artificielle",
    "python",
    "cybersecurite",
    "reseaux sociaux",
    "innovation",
    "economie",
    "sport",
    "politique",
    "sante",
    "education",
    "environnement",
    "climat",
    "agriculture",
    "technologie",
    "culture",
    "cinema",
    "musique",
    "emploi",
    "startup",
    "fintech",
    "blockchain",
    "crypto",
    "5G",
    "telecom",
    "energie",
    "elections",
    "droits des femmes",
    "jeunesse",
    "handicap",
    "immigration",
    "terrorisme",
    "corruption",
    "justice",
    "transport",
    "tourisme",
]

# ============================================================
# CSS PREMIUM
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #eef7fa 0%, #e8f4f8 100%) !important;
    }
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
    }
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem !important;
        max-width: 100% !important;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #0f172a !important;
    }
    div[data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06),
                    0 1px 3px rgba(15, 23, 42, 0.04) !important;
        border: 1px solid rgba(15, 23, 42, 0.03) !important;
        margin-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FONCTIONS PREMIUM
# ============================================================

def kpi_card(icone, label, valeur, tendance=None, couleur=None):
    if couleur is None:
        couleur = C_PRIMAIRE

    if tendance:
        trend_html = (
            '<div style="display: inline-block; '
            'background: rgba(39, 174, 96, 0.12); '
            'color: #27ae60; padding: 5px 12px; '
            'border-radius: 20px; '
            'font-size: 0.75rem; font-weight: 700;">'
            f'↑ {tendance}'
            '</div>'
        )
    else:
        trend_html = ""

    html = (
        '<div style="'
        'background: #ffffff; '
        'border-radius: 20px; '
        'padding: 22px 24px; '
        'box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04); '
        'border: 1px solid rgba(15, 23, 42, 0.03); '
        'height: 100%; '
        'min-height: 155px; '
        'position: relative; '
        'overflow: hidden;'
        '">'
        '<div style="'
        'position: absolute; '
        'top: 0; left: 0; right: 0; '
        'height: 4px; '
        f'background: {couleur}; '
        'border-radius: 20px 20px 0 0;'
        '"></div>'
        '<div style="'
        'display: flex; '
        'align-items: center; '
        'gap: 12px; '
        'margin-bottom: 16px;'
        '">'
        '<div style="'
        'width: 40px; height: 40px; '
        f'background: {couleur}15; '
        'border-radius: 12px; '
        'display: flex; align-items: center; justify-content: center; '
        'font-size: 1.2rem;'
        '">'
        f'{icone}'
        '</div>'
        '<div style="'
        'font-size: 0.72rem; '
        'color: #64748b; '
        'font-weight: 700; '
        'text-transform: uppercase; '
        'letter-spacing: 0.8px;'
        '">'
        f'{label}'
        '</div>'
        '</div>'
        '<div style="'
        'font-size: 2.2rem; '
        'font-weight: 800; '
        'color: #0f172a; '
        'line-height: 1; '
        'letter-spacing: -1px; '
        'margin-bottom: 12px;'
        '">'
        f'{valeur}'
        '</div>'
        f'{trend_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_titre(icone, titre, sous_titre=""):
    html = (
        '<div style="margin: 40px 0 20px 0;">'
        '<h2 style="'
        'margin: 0; '
        'font-size: 1.35rem; '
        'color: #0f172a; '
        'font-weight: 800; '
        'display: flex; '
        'align-items: center; '
        'gap: 12px; '
        'letter-spacing: -0.3px;'
        '">'
        f'<span style="font-size: 1.5rem;">{icone}</span>'
        f'<span>{titre}</span>'
        '</h2>'
    )
    if sous_titre:
        html += (
            '<p style="'
            'margin: 6px 0 0 44px; '
            'color: #64748b; '
            'font-size: 0.85rem; '
            'font-weight: 500;'
            '">'
            f'{sous_titre}'
            '</p>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def carte_article(titre, source, date, description, url, image_url):
    image_html = ""
    if image_url:
        image_html = (
            '<div style="'
            'width: 100%; height: 180px; '
            'border-radius: 14px 14px 0 0; '
            'overflow: hidden; background: #f1f5f9;'
            '">'
            f'<img src="{image_url}" '
            'style="width: 100%; height: 100%; object-fit: cover;" '
            'onerror="this.style.display=\'none\'"/>'
            '</div>'
        )
    else:
        image_html = (
            '<div style="'
            'width: 100%; height: 100px; '
            'border-radius: 14px 14px 0 0; '
            'background: linear-gradient(135deg, #e70013 0%, #b8000f 100%); '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-size: 2rem;'
            '">📰</div>'
        )

    desc_html = ""
    if description:
        desc_court = description[:140] + ("..." if len(description) > 140 else "")
        desc_html = (
            '<p style="'
            'color: #475569; font-size: 0.85rem; '
            'line-height: 1.5; margin: 10px 0 0 0;'
            '">'
            f'{desc_court}'
            '</p>'
        )

    html = (
        '<div style="'
        'background: #ffffff; border-radius: 14px; overflow: hidden; '
        'box-shadow: 0 2px 12px rgba(15, 23, 42, 0.06); '
        'margin-bottom: 16px; '
        'border: 1px solid rgba(15, 23, 42, 0.04);'
        '">'
        f'{image_html}'
        '<div style="padding: 16px 18px;">'
        '<div style="'
        'font-size: 0.7rem; color: #e70013; font-weight: 700; '
        'text-transform: uppercase; letter-spacing: 0.8px; '
        'margin-bottom: 8px;'
        '">'
        f'📰 {source} • {date[:10]}'
        '</div>'
        f'<a href="{url}" target="_blank" style="'
        'color: #0f172a; text-decoration: none; '
        'font-weight: 700; font-size: 0.98rem; '
        'line-height: 1.4; display: block;'
        '">'
        f'{titre}'
        '</a>'
        f'{desc_html}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# EN-TÊTE
# ============================================================
style.page_header(
    titre="Actualités",
    icone="📰",
    description="Recherche intelligente par média, sujet ou thème — Sources NewsAPI + base TuniWatch",
    badge="LIVE"
)

# ============================================================
# VÉRIFICATION CONFIG
# ============================================================
if not est_configure():
    st.error("⚠️ Clé API NewsAPI non configurée.")
    st.info("Ajoutez votre clé dans le fichier `.env` : `NEWSAPI_KEY=votre_cle`")
    st.stop()

# ============================================================
# CHARGEMENT DES MÉDIAS DE LA BASE
# ============================================================
try:
    with st.spinner("Chargement des médias..."):
        medias_db = cockpit_stats.liste_sources_actives()
    medias_ok = True
except Exception:
    medias_ok = False
    medias_db = []

# ============================================================
# SECTION 1 : FILTRES
# ============================================================
section_titre("🎛️", "Filtres de recherche", "Recherche intelligente avec détection dès 2 lettres")

col1, col2, col3 = st.columns([2, 1, 1])

# ---------- TYPE DE RECHERCHE ----------
with col1:
    type_recherche = st.radio(
        "🎯 Type de recherche",
        options=["📺 Par média", "🔍 Par sujet / thème", "✏️ Recherche libre"],
        horizontal=True,
        key="news_type_recherche"
    )

# ---------- SUJET / MÉDIA ----------
mots_cles = []

if type_recherche == "📺 Par média":
    # --- Recherche rapide média ---
    st.markdown("##### 🔎 Recherche rapide dans les médias")
    recherche_media = st.text_input(
        "Tapez 2 lettres ou plus pour filtrer",
        placeholder="Ex: tun, mos, afr...",
        key="news_search_media",
        label_visibility="collapsed"
    )

    if medias_ok and medias_db:
        # Filtre la liste selon la recherche
        if recherche_media and len(recherche_media) >= 2:
            medias_filtres = [m for m in medias_db
                              if recherche_media.lower() in m.lower()]
        else:
            medias_filtres = medias_db

        if medias_filtres:
            media_choisi = st.selectbox(
                f"📺 Choisir un média ({len(medias_filtres)} résultats)",
                options=["🌐 Tous les médias"] + medias_filtres,
                index=0,
                key="news_media_select"
            )
            if media_choisi != "🌐 Tous les médias":
                mots_cles = [media_choisi]
        else:
            st.warning(f"Aucun média trouvé pour « {recherche_media} »")
            media_choisi = "🌐 Tous les médias"
    else:
        st.warning("⚠️ Impossible de charger les médias depuis la base.")
        media_choisi = "🌐 Tous les médias"

elif type_recherche == "🔍 Par sujet / thème":
    # --- Recherche rapide sujet ---
    st.markdown("##### 🔎 Recherche rapide dans les sujets")
    recherche_sujet = st.text_input(
        "Tapez 2 lettres ou plus pour filtrer",
        placeholder="Ex: pol, spo, ia...",
        key="news_search_sujet",
        label_visibility="collapsed"
    )

    if recherche_sujet and len(recherche_sujet) >= 2:
        sujets_filtres = [s for s in SUJETS_PREDEFINIS
                          if recherche_sujet.lower() in s.lower()]
    else:
        sujets_filtres = SUJETS_PREDEFINIS

    if sujets_filtres:
        sujet_choisi = st.selectbox(
            f"🔍 Choisir un sujet ({len(sujets_filtres)} résultats)",
            options=sujets_filtres,
            index=0,
            key="news_sujet_select"
        )
        mots_cles = [sujet_choisi]
    else:
        st.warning(f"Aucun sujet trouvé pour « {recherche_sujet} »")

else:  # Recherche libre
    sujet_perso = st.text_input(
        "✏️ Recherche libre (séparez plusieurs mots par des virgules)",
        placeholder="Ex: climat, énergie, santé",
        key="news_sujet_libre"
    )
    if sujet_perso:
        mots_cles = [s.strip() for s in sujet_perso.split(",") if s.strip()]
    else:
        mots_cles = ["Tunisie"]

# ---------- NOMBRE D'ARTICLES ----------
with col2:
    nb_articles = st.slider(
        "📊 Nombre d'articles",
        min_value=5, max_value=50, value=15, step=5,
        key="news_nb"
    )

# ---------- PÉRIODE ----------
with col3:
    jours = st.selectbox(
        "📅 Période",
        [1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"{x} jours",
        key="news_jours"
    )

# ---------- BOUTONS ----------
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    if st.button("🔄 Récupérer les news", use_container_width=True, type="primary", key="news_bouton"):
        st.cache_data.clear()
        st.rerun()

with col_btn2:
    if st.button("🗑️ Vider le cache", use_container_width=True, key="news_clear"):
        st.cache_data.clear()
        st.success("Cache vidé !")

# ---------- INFO FILTRE ACTIF ----------
if not mots_cles:
    st.warning("⚠️ Sélectionnez un média ou un sujet pour lancer la recherche.")
    st.stop()

st.info(f"🎯 **Recherche active** : {', '.join(mots_cles)}")

# ============================================================
# SECTION 2 : RÉCUPÉRATION DES NEWS
# ============================================================

@st.cache_data(ttl=300)
def charger_news(mots_cles_tuple, nb, jours):
    articles = recuperer_news_multi(list(mots_cles_tuple), nb_par_mot=nb, jours=jours)
    if articles:
        try:
            import db
            db.sauvegarder_articles(articles)
        except Exception:
            pass
    return articles

with st.spinner("⏳ Récupération des articles en cours..."):
    articles = charger_news(tuple(mots_cles), nb_articles, jours)

if not articles:
    st.warning(f"Aucun article trouvé pour : {', '.join(mots_cles)}")
    st.info("💡 Essayez avec un autre média, un autre sujet ou augmentez la période.")
    st.stop()

df = pd.DataFrame(articles)

# ============================================================
# SECTION 3 : KPI
# ============================================================
section_titre("📊", "Résultats de la recherche", f"Critères : {', '.join(mots_cles)}")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    kpi_card("📰", "Articles trouvés", len(df), couleur=C_PRIMAIRE)

with col2:
    kpi_card("🌐", "Sources uniques", df["source"].nunique(), couleur=C_TEAL)

with col3:
    kpi_card("🔑", "Mots-clés", len(mots_cles), couleur=C_JAUNE)

with col4:
    source_top = df["source"].value_counts().index[0] if len(df) > 0 else "—"
    kpi_card("🏆", "Top source", source_top[:20], couleur=C_VIOLET)

# ============================================================
# SECTION 4 : FILTRES POST-RÉCUPÉRATION
# ============================================================
section_titre("🔍", "Affiner les résultats", "Filtrez la liste ci-dessous")

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

df_filtre = df.copy()
if source_filtre != "Toutes":
    df_filtre = df_filtre[df_filtre["source"] == source_filtre]
if recherche_titre:
    df_filtre = df_filtre[
        df_filtre["titre"].str.contains(recherche_titre, case=False, na=False)
    ]

st.caption(f"**{len(df_filtre)}** article(s) affiché(s) après filtrage")

# ============================================================
# SECTION 5 : LISTE DES ARTICLES EN CARTES
# ============================================================
section_titre("📄", "Articles", "Cliquez sur un titre pour ouvrir l'article")

if len(df_filtre) == 0:
    st.info("Aucun article ne correspond aux filtres.")
else:
    nb_cols = 3
    cols = st.columns(nb_cols, gap="medium")

    for i, (_, article) in enumerate(df_filtre.iterrows()):
        col = cols[i % nb_cols]
        with col:
            carte_article(
                titre=article.get("titre", "Sans titre"),
                source=article.get("source", "Inconnue"),
                date=article.get("date", ""),
                description=article.get("description", ""),
                url=article.get("url", "#"),
                image_url=article.get("image", None)
            )

# ============================================================
# SECTION 6 : EXPORT
# ============================================================
section_titre("📥", "Exporter les résultats", "Télécharger la liste filtrée")

csv = df_filtre.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Télécharger en CSV",
    data=csv,
    file_name=f"news_{mots_cles[0].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    use_container_width=False
)

# ============================================================
# FOOTER
# ============================================================
style.footer()