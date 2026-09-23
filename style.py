# ============================================================
# TuniWatch - Style Professionnel (v2)
# Fichier : style.py
# Description : CSS personnalisé et thème visuel premium
# ============================================================

import streamlit as st


def apply_style():
    """Applique le style CSS personnalisé à l'application."""

    # Police Inter chargée proprement
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* ============================================================
           POLICE UNIVERSELLE
           ============================================================ */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ============================================================
           VARIABLES
           ============================================================ */
        :root {
            --primary: #E63946;
            --primary-dark: #C1121F;
            --secondary: #1D3557;
            --success: #06D6A0;
            --warning: #FFD166;
            --danger: #EF476F;
            --text-dark: #1D3557;
            --text-muted: #6C757D;
            --border: #E9ECEF;
            --bg-light: #F8F9FA;
            --radius: 16px;
        }

        /* ============================================================
           CONTENEUR PRINCIPAL - PLUS D'AIR
           ============================================================ */
        .main .block-container {
            padding-top: 2.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 1500px !important;
        }

        /* ============================================================
           TITRES
           ============================================================ */
        h1 {
            color: #1D3557 !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.8px !important;
            margin-bottom: 0.3rem !important;
        }

        h2 {
            color: #1D3557 !important;
            font-weight: 700 !important;
            font-size: 1.5rem !important;
            letter-spacing: -0.4px !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }

        h3, h5 {
            color: #1D3557 !important;
            font-weight: 700 !important;
        }

        /* Caption */
        .stCaption, [data-testid="stCaptionContainer"] {
            color: #6C757D !important;
            font-size: 0.9rem !important;
        }

        /* ============================================================
           SIDEBAR - DÉGRADÉ BLEU NUIT
           ============================================================ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1D3557 0%, #0E1117 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05) !important;
        }

        section[data-testid="stSidebar"] * {
            color: #FAFAFA !important;
        }

        /* Le bloc utilisateur (superadmin) - on neutralise le rouge */
        section[data-testid="stSidebar"] .stMarkdown div[style*="background"] {
            background: rgba(230, 57, 70, 0.15) !important;
            border: 1px solid rgba(230, 57, 70, 0.4) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }

        /* Navigation */
        section[data-testid="stSidebar"] nav ul li a {
            border-radius: 10px !important;
            padding: 0.6rem 1rem !important;
            margin: 0.15rem 0 !important;
            transition: all 0.2s ease !important;
            font-weight: 500 !important;
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

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1) !important;
        }

        /* ============================================================
           CARTES KPI - PREMIUM
           ============================================================ */
        .kpi-card {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04) !important;
            border: 1px solid #E9ECEF !important;
            border-left: 5px solid #E63946 !important;
            transition: all 0.3s ease !important;
            height: 100% !important;
            position: relative !important;
            overflow: hidden !important;
        }

        .kpi-card::after {
            content: '' !important;
            position: absolute !important;
            top: -40px !important;
            right: -40px !important;
            width: 120px !important;
            height: 120px !important;
            background: radial-gradient(circle, rgba(230,57,70,0.06) 0%, transparent 70%) !important;
            border-radius: 50% !important;
        }

        .kpi-card:hover {
            transform: translateY(-6px) !important;
            box-shadow: 0 12px 28px rgba(0,0,0,0.1) !important;
        }

        .kpi-icon {
            font-size: 1.6rem !important;
            margin-bottom: 0.75rem !important;
            display: block !important;
        }

        .kpi-label {
            font-size: 0.72rem !important;
            color: #6C757D !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            font-weight: 700 !important;
            margin-bottom: 0.6rem !important;
        }

        .kpi-value {
            font-size: 2.2rem !important;
            font-weight: 900 !important;
            color: #1D3557 !important;
            line-height: 1 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -1px !important;
        }

        .kpi-trend {
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.3rem !important;
            padding: 0.25rem 0.65rem !important;
            border-radius: 20px !important;
        }

        .kpi-trend.positive {
            color: #06D6A0 !important;
            background: rgba(6, 214, 160, 0.12) !important;
        }

        .kpi-trend.negative {
            color: #EF476F !important;
            background: rgba(239, 71, 111, 0.12) !important;
        }

        .kpi-trend.neutral {
            color: #B8860B !important;
            background: rgba(255, 209, 102, 0.15) !important;
        }

        /* ============================================================
           CARTES D'ARTICLES
           ============================================================ */
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
            font-weight: 600 !important;
            color: #1D3557 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.5rem !important;
            line-height: 1.4 !important;
        }

        .article-meta {
            font-size: 0.78rem !important;
            color: #6C757D !important;
            display: flex !important;
            gap: 0.8rem !important;
            flex-wrap: wrap !important;
            align-items: center !important;
        }

        .article-badge {
            display: inline-block !important;
            padding: 0.15rem 0.6rem !important;
            border-radius: 20px !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        .badge-positif { background: rgba(6, 214, 160, 0.15) !important; color: #06D6A0 !important; }
        .badge-negatif { background: rgba(239, 71, 111, 0.15) !important; color: #EF476F !important; }
        .badge-neutre  { background: rgba(255, 209, 102, 0.2) !important;  color: #B8860B !important; }

        /* ============================================================
           BOUTONS
           ============================================================ */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.4rem !important;
            transition: all 0.2s ease !important;
            border: none !important;
            background: #E63946 !important;
            color: white !important;
            box-shadow: 0 2px 8px rgba(230, 57, 70, 0.2) !important;
        }

        .stButton > button:hover {
            background: #C1121F !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(230, 57, 70, 0.3) !important;
        }

        /* ============================================================
           SÉPARATEURS VISIBLES
           ============================================================ */
        hr {
            border: none !important;
            border-top: 1px solid #E9ECEF !important;
            margin: 2.5rem 0 !important;
        }

        /* ============================================================
           SCROLLBAR
           ============================================================ */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #F8F9FA; }
        ::-webkit-scrollbar-thumb { background: #CED4DA; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #ADB5BD; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# COMPOSANTS
# ============================================================

def kpi_card(icon: str, label: str, value: str, trend: str = None, trend_type: str = "positive"):
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


def article_card(titre: str, source: str, date: str = "", sentiment: str = None, url: str = None):
    """Affiche une carte d'article professionnelle."""
    badge_html = ""
    if sentiment:
        badge_class = f"badge-{sentiment}"
        badge_html = f'<span class="article-badge {badge_class}">{sentiment}</span>'

    link_html = f'<a href="{url}" target="_blank" style="color:#E63946; text-decoration:none;">🔗</a>' if url else ''

    st.markdown(f"""
    <div class="article-card">
        <div class="article-title">{titre}</div>
        <div class="article-meta">
            <span>📰 {source}</span>
            {f'<span>📅 {date}</span>' if date else ''}
            {badge_html}
            {link_html}
        </div>
    </div>
    """, unsafe_allow_html=True)