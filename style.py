# ============================================================
# TuniWatch - Style Professionnel (v6 - FINAL)
# Fichier : style.py
# Description : CSS premium + alias pour compatibilité
# ============================================================

import streamlit as st
import re


# ============================================================
# 🔧 NETTOYAGE HTML (sans toucher aux accents)
# ============================================================
def nettoyer_html(texte):
    """
    Nettoie UNIQUEMENT les balises HTML résiduelles.
    NE TOUCHE PAS aux accents ni aux apostrophes.
    """
    if not texte:
        return ""
    texte = str(texte)
    # Retirer uniquement les balises HTML
    texte = re.sub(r'<[^>]+>', '', texte)
    # Décoder quelques entités HTML basiques
    texte = texte.replace('&amp;', '&')
    texte = texte.replace('&lt;', '<')
    texte = texte.replace('&gt;', '>')
    texte = texte.replace('&quot;', '"')
    texte = texte.replace('&nbsp;', ' ')
    # Réduire les espaces multiples
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()


# ============================================================
# 🎨 APPLICATION DU STYLE
# ============================================================
def apply_style():
    """Applique le style CSS personnalisé à l'application."""

    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* POLICE */
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

        /* CONTENEUR */
        .main .block-container {
            padding-top: 2.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 1500px !important;
        }

        /* TITRES */
        h1 { color: #1D3557 !important; font-weight: 800 !important; font-size: 2.2rem !important; letter-spacing: -0.8px !important; }
        h2 { color: #1D3557 !important; font-weight: 700 !important; font-size: 1.5rem !important; letter-spacing: -0.4px !important; }
        h3, h5 { color: #1D3557 !important; font-weight: 700 !important; }
        .stCaption, [data-testid="stCaptionContainer"] { color: #6C757D !important; font-size: 0.9rem !important; }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1D3557 0%, #0E1117 100%) !important;
        }
        section[data-testid="stSidebar"] * { color: #FAFAFA !important; }
        section[data-testid="stSidebar"] nav ul li a {
            border-radius: 10px !important;
            padding: 0.6rem 1rem !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] nav ul li a:hover {
            background: rgba(230, 57, 70, 0.2) !important;
            transform: translateX(4px) !important;
        }
        section[data-testid="stSidebar"] nav ul li a[aria-current="page"] {
            background: rgba(230, 57, 70, 0.35) !important;
            border-left: 4px solid #E63946 !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }

        /* CARTES KPI */
        .kpi-card {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04) !important;
            border: 1px solid #E9ECEF !important;
            border-left: 5px solid #E63946 !important;
            transition: all 0.3s ease !important;
            height: 100% !important;
        }
        .kpi-card:hover {
            transform: translateY(-6px) !important;
            box-shadow: 0 12px 28px rgba(0,0,0,0.1) !important;
        }
        .kpi-icon { font-size: 1.6rem !important; margin-bottom: 0.75rem !important; display: block !important; }
        .kpi-label {
            font-size: 0.72rem !important; color: #6C757D !important;
            text-transform: uppercase !important; letter-spacing: 1.5px !important;
            font-weight: 700 !important; margin-bottom: 0.6rem !important;
        }
        .kpi-value {
            font-size: 2.2rem !important; font-weight: 900 !important;
            color: #1D3557 !important; line-height: 1 !important;
            margin-bottom: 0.5rem !important; letter-spacing: -1px !important;
        }
        .kpi-trend {
            font-size: 0.75rem !important; font-weight: 700 !important;
            display: inline-flex !important; align-items: center !important;
            gap: 0.3rem !important; padding: 0.25rem 0.65rem !important;
            border-radius: 20px !important;
        }
        .kpi-trend.positive { color: #06D6A0 !important; background: rgba(6, 214, 160, 0.12) !important; }
        .kpi-trend.negative { color: #EF476F !important; background: rgba(239, 71, 111, 0.12) !important; }
        .kpi-trend.neutral { color: #B8860B !important; background: rgba(255, 209, 102, 0.15) !important; }

        /* CARTES ARTICLES */
        .article-card {
            background: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 0.75rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
            border: 1px solid #E9ECEF !important;
            border-left: 4px solid transparent !important;
            transition: all 0.2s ease !important;
        }
        .article-card:hover {
            box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
            border-left-color: #E63946 !important;
            transform: translateX(4px) !important;
        }
        .article-title {
            font-weight: 600 !important; color: #1D3557 !important;
            font-size: 0.95rem !important; margin-bottom: 0.5rem !important;
            line-height: 1.4 !important;
        }
        .article-meta {
            font-size: 0.78rem !important; color: #6C757D !important;
            display: flex !important; gap: 0.8rem !important;
            flex-wrap: wrap !important; align-items: center !important;
        }
        .article-badge {
            display: inline-block !important; padding: 0.15rem 0.6rem !important;
            border-radius: 20px !important; font-size: 0.68rem !important;
            font-weight: 700 !important; text-transform: uppercase !important;
        }
        .badge-positif { background: rgba(6, 214, 160, 0.15) !important; color: #06D6A0 !important; }
        .badge-negatif { background: rgba(239, 71, 111, 0.15) !important; color: #EF476F !important; }
        .badge-neutre  { background: rgba(255, 209, 102, 0.2) !important;  color: #B8860B !important; }

        /* BOUTONS */
        .stButton > button {
            border-radius: 10px !important; font-weight: 600 !important;
            padding: 0.55rem 1.4rem !important; transition: all 0.2s ease !important;
            border: none !important; background: #E63946 !important;
            color: white !important; box-shadow: 0 2px 8px rgba(230, 57, 70, 0.2) !important;
        }
        .stButton > button:hover {
            background: #C1121F !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(230, 57, 70, 0.3) !important;
        }

        /* SEPARATEURS */
        hr { border: none !important; border-top: 1px solid #E9ECEF !important; margin: 2.5rem 0 !important; }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #F8F9FA; }
        ::-webkit-scrollbar-thumb { background: #CED4DA; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 🧩 COMPOSANTS RÉUTILISABLES
# ============================================================
def kpi_card(icon: str, label: str, value: str, trend: str = None, trend_type: str = "positive", **kwargs):
    """Affiche une carte KPI professionnelle."""
    trend_html = ""
    if trend:
        trend_html = f'<span class="kpi-trend {trend_type}">{trend}</span>'

    st.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def article_card(titre: str, source: str = "", date: str = "", sentiment: str = None, url: str = None, **kwargs):
    """
    Affiche une carte d'article professionnelle.
    ⚠️ AUCUNE transformation d'encodage : on affiche le titre TEL QUEL.
    """
    # On retire UNIQUEMENT le HTML, PAS les accents ni apostrophes
    titre_propre = nettoyer_html(titre)
    source_propre = nettoyer_html(source)
    date_propre = str(date or "").strip()

    if not titre_propre:
        titre_propre = "(Titre non disponible)"

    # Badge de sentiment
    badge_html = ""
    if sentiment:
        sentiment_clean = str(sentiment).lower().strip()
        if sentiment_clean in ("positif", "negatif", "neutre"):
            badge_html = f'<span class="article-badge badge-{sentiment_clean}">{sentiment_clean}</span>'

    # Lien
    url_clean = str(url or "").strip()
    link_html = (
        f'<a href="{url_clean}" target="_blank" rel="noopener" '
        f'style="color:#E63946; text-decoration:none; font-weight:600;">🔗 Lire</a>'
    ) if url_clean else ''

    # Métadonnées
    meta_parts = [f'<span>📰 {source_propre}</span>']
    if date_propre:
        meta_parts.append(f'<span>📅 {date_propre[:10]}</span>')
    if badge_html:
        meta_parts.append(badge_html)
    if link_html:
        meta_parts.append(link_html)

    meta_html = " ".join(meta_parts)

    st.markdown(f"""
    <div class="article-card">
        <div class="article-title">{titre_propre}</div>
        <div class="article-meta">
            {meta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 🔗 ALIAS POUR COMPATIBILITÉ
# (les anciennes pages appellent style.appliquer_style(),
#  style.section_title() et style.footer())
# ============================================================

def appliquer_style():
    """Alias de apply_style() pour compatibilité avec les anciennes pages."""
    return apply_style()


def section_title(icone, titre, sous_titre=""):
    """Affiche un titre de section avec icône."""
    st.markdown(f"## {icone} {titre}")
    if sous_titre:
        st.caption(sous_titre)
    st.markdown("")


def footer():
    """Affiche le pied de page."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#6C757D; font-size:0.8rem; padding:1rem;'>"
        "🇹🇳 <b>TuniWatch</b> © 2026 — Observatoire des médias en Tunisie"
        "</div>",
        unsafe_allow_html=True
    )