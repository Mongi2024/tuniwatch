# ============================================================
# TuniWatch - Style Professionnel (v8 - avec sidebar user)
# Fichier : style.py
# Description : CSS premium + sidebar utilisateur + déconnexion
# ============================================================

import streamlit as st
import re


# ============================================================
# 🔧 NETTOYAGE HTML
# ============================================================
def nettoyer_html(texte):
    """Nettoie UNIQUEMENT les balises HTML résiduelles."""
    if not texte:
        return ""
    texte = str(texte)
    texte = re.sub(r'<[^>]+>', '', texte)
    texte = texte.replace('&amp;', '&')
    texte = texte.replace('&lt;', '<')
    texte = texte.replace('&gt;', '>')
    texte = texte.replace('&quot;', '"')
    texte = texte.replace('&nbsp;', ' ')
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()


# ============================================================
# 👤 BLOC UTILISATEUR DANS LA SIDEBAR
# ============================================================
def sidebar_user():
    """
    Affiche le bloc utilisateur connecté en haut de la sidebar
    avec un bouton de déconnexion.
    """
    user = st.session_state.get("user")
    if not user:
        return

    login = user.get("login", "Utilisateur")
    role = user.get("role", "user")

    # Emoji selon le rôle
    emoji_role = {
        "super_admin": "👑",
        "admin": "🛡️",
        "editeur": "✏️",
        "lecteur": "👤",
        "user": "👤",
    }.get(role, "👤")

    # Libellé du rôle en français
    label_role = {
        "super_admin": "Super Admin",
        "admin": "Administrateur",
        "editeur": "Éditeur",
        "lecteur": "Lecteur",
        "user": "Utilisateur",
    }.get(role, role)

    # Avatar : première lettre en majuscule
    initiale = login[0].upper() if login else "?"

    # Bloc HTML utilisateur
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(230, 57, 70, 0.15) 0%, rgba(230, 57, 70, 0.05) 100%);
        border: 1px solid rgba(230, 57, 70, 0.3);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: #E63946;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.1rem;
            flex-shrink: 0;
        ">{initiale}</div>
        <div style="flex: 1; overflow: hidden;">
            <div style="
                color: #FFFFFF;
                font-weight: 700;
                font-size: 0.9rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{login}</div>
            <div style="
                color: #FFD166;
                font-size: 0.75rem;
                font-weight: 600;
            ">{emoji_role} {label_role}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Bouton de déconnexion
    if st.sidebar.button(
        "🚪 Se déconnecter",
        use_container_width=True,
        key="btn_logout_sidebar"
    ):
        # Nettoyer la session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Séparateur
    st.sidebar.markdown("---")


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
        /* Police principale */
        html, body, .stApp, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ⚠️ NE PAS toucher aux polices des icônes Streamlit */
        [class*="material-symbols"],
        [class*="Material Symbols"],
        [data-testid="stIconMaterial"],
        span[translate="no"] {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        }

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

        /* Bouton déconnexion (sidebar) */
        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(230, 57, 70, 0.15) !important;
            border: 1px solid rgba(230, 57, 70, 0.4) !important;
            color: #FF6B6B !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(230, 57, 70, 0.35) !important;
            color: #FFFFFF !important;
        }

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

        /* BOUTONS (contenu principal) */
        .main .stButton > button {
            border-radius: 10px !important; font-weight: 600 !important;
            padding: 0.55rem 1.4rem !important; transition: all 0.2s ease !important;
            border: none !important; background: #E63946 !important;
            color: white !important; box-shadow: 0 2px 8px rgba(230, 57, 70, 0.2) !important;
        }
        .main .stButton > button:hover {
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
def kpi_card(icon, label, value, trend=None, trend_type="positive",
             tendance=None, couleur=None, **kwargs):
    """Affiche une carte KPI professionnelle."""
    if trend is None and tendance is not None:
        trend = tendance

    border_style = f"border-left: 5px solid {couleur} !important;" if couleur else ""

    trend_html = ""
    if trend:
        trend_html = f'<span class="kpi-trend {trend_type}">{trend}</span>'

    st.markdown(f"""
    <div class="kpi-card" style="{border_style}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def article_card(titre, source="", date="", sentiment=None, url=None, **kwargs):
    """Affiche une carte d'article professionnelle."""
    titre_propre = nettoyer_html(titre)
    source_propre = nettoyer_html(source)
    date_propre = str(date or "").strip()

    if not titre_propre:
        titre_propre = "(Titre non disponible)"

    badge_html = ""
    if sentiment:
        sentiment_clean = str(sentiment).lower().strip()
        if sentiment_clean in ("positif", "negatif", "neutre"):
            badge_html = f'<span class="article-badge badge-{sentiment_clean}">{sentiment_clean}</span>'

    url_clean = str(url or "").strip()
    link_html = (
        f'<a href="{url_clean}" target="_blank" rel="noopener" '
        f'style="color:#E63946; text-decoration:none; font-weight:600;">🔗 Lire</a>'
    ) if url_clean else ''

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
# ============================================================

def appliquer_style():
    """Alias de apply_style() pour compatibilité."""
    return apply_style()


def section_title(icone, titre, sous_titre=""):
    """Affiche un titre de section avec icône."""
    st.markdown(f"## {icone} {titre}")
    if sous_titre:
        st.caption(sous_titre)
    st.markdown("")


def page_header(titre, icone="", description="", badge=None):
    """Affiche un en-tête de page premium."""
    badge_html = ""
    if badge:
        badge_html = (
            f'<span style="display:inline-block; padding:0.15rem 0.6rem; '
            f'background:rgba(230,57,70,0.12); color:#E63946; '
            f'border-radius:20px; font-size:0.75rem; font-weight:700; '
            f'margin-left:0.5rem;">{badge}</span>'
        )

    st.markdown(f"""
    <div style="padding: 1rem 0 1.5rem 0;">
        <h1 style="margin:0; color:#1D3557; font-weight:800; font-size:2.4rem; letter-spacing:-1px;">
            {icone} {titre} {badge_html}
        </h1>
        <p style="color:#6C757D; font-size:1rem; margin-top:0.5rem; margin-bottom:0;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def footer():
    """Affiche le pied de page."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#6C757D; font-size:0.8rem; padding:1rem;'>"
        "🇹🇳 <b>TuniWatch</b> © 2026 — Observatoire des médias en Tunisie"
        "</div>",
        unsafe_allow_html=True
    )