# ============================================================
# TuniWatch - Style Professionnel (v22 - CORRIGÉ)
# Fichier : style.py
# ============================================================

import streamlit as st
import re


def nettoyer_html(texte):
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


def apply_style():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* ============ POLICE ============ */
        html, body, .stApp, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        [class*="material-symbols"],
        [class*="Material Symbols"],
        [data-testid="stIconMaterial"],
        span[translate="no"] {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        }

        /* ============ CONTENEUR ============ */
        .main .block-container {
            padding-top: 3rem !important;
            padding-bottom: 3rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 1500px !important;
        }

        /* ============ ⚡ ANTI-VIBRATION ============ */
        .js-plotly-plot,
        .js-plotly-plot *,
        .plot-container,
        .plot-container *,
        .svg-container,
        .svg-container *,
        .main-svg,
        .main-svg * {
            transition: none !important;
            animation: none !important;
            -webkit-transition: none !important;
            -webkit-animation: none !important;
        }
        .js-plotly-plot .trace,
        .js-plotly-plot .scatterlayer,
        .js-plotly-plot .barlayer,
        .js-plotly-plot .pielayer {
            opacity: 1 !important;
        }
        .kpi-card, .article-card, .main .stButton > button {
            transition: all 0.2s ease !important;
        }

        /* ============ TITRES ============ */
        h1 { color: #1D3557 !important; font-weight: 800 !important; font-size: 2.2rem !important; letter-spacing: -0.8px !important; }
        h2 { color: #1D3557 !important; font-weight: 700 !important; font-size: 1.5rem !important; letter-spacing: -0.4px !important; }
        h3, h5 { color: #1D3557 !important; font-weight: 700 !important; }
        .stCaption, [data-testid="stCaptionContainer"] { color: #6C757D !important; font-size: 0.9rem !important; }

        /* ============ SIDEBAR ============ */
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
        section[data-testid="stSidebar"] details {
            background: linear-gradient(135deg, rgba(230, 57, 70, 0.2) 0%, rgba(230, 57, 70, 0.06) 100%) !important;
            border: 1px solid rgba(230, 57, 70, 0.4) !important;
            border-radius: 12px !important;
            margin-bottom: 12px !important;
            padding: 4px 8px !important;
        }
        section[data-testid="stSidebar"] details summary {
            font-weight: 700 !important;
            color: #FFD166 !important;
            padding: 8px 4px !important;
        }
        section[data-testid="stSidebar"] details .stButton > button {
            background: linear-gradient(135deg, #e70013 0%, #b8000f 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            width: 100% !important;
            margin-top: 8px !important;
        }

        /* ============ GRAPHIQUES PLOTLY ============ */
        div[data-testid="stPlotlyChart"] {
            padding: 8px !important;
            border-radius: 16px !important;
            background: #FFFFFF !important;
            box-shadow: 0 2px 12px rgba(15, 23, 42, 0.06) !important;
            overflow: visible !important;
            margin-bottom: 16px !important;
        }
        div[data-testid="stPlotlyChart"] > div {
            overflow: visible !important;
        }

        /* ============ CARTES KPI ============ */
        .kpi-card {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04) !important;
            border: 1px solid #E9ECEF !important;
            border-left: 5px solid #E63946 !important;
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

        /* ============ CARTES ARTICLES ============ */
        .article-card {
            background: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 0.75rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
            border: 1px solid #E9ECEF !important;
            border-left: 4px solid transparent !important;
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

        /* ============ BOUTONS ============ */
        .main .stButton > button {
            border-radius: 10px !important; font-weight: 600 !important;
            padding: 0.55rem 1.4rem !important;
            border: none !important; background: #E63946 !important;
            color: white !important; box-shadow: 0 2px 8px rgba(230, 57, 70, 0.2) !important;
        }
        .main .stButton > button:hover {
            background: #C1121F !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(230, 57, 70, 0.3) !important;
        }

        hr { border: none !important; border-top: 1px solid #E9ECEF !important; margin: 2.5rem 0 !important; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #F8F9FA; }
        ::-webkit-scrollbar-thumb { background: #CED4DA; border-radius: 4px; }
        .stDeployButton { display: none !important; }
        #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 👤 BLOC UTILISATEUR
# ============================================================
def sidebar_user():
    import auth
    user = st.session_state.get("user")
    if not user:
        return
    login = user.get("login", "Utilisateur")
    role = user.get("role", "user")
    emoji_role = {"super_admin": "👑", "admin": "🛡️", "editeur": "✏️",
                  "lecteur": "👤", "viewer": "👤", "user": "👤"}.get(role, "👤")
    label_role = {"super_admin": "Super Admin", "admin": "Administrateur",
                  "editeur": "Éditeur", "lecteur": "Lecteur",
                  "viewer": "Lecteur", "user": "Utilisateur"}.get(role, role)
    initiale = login[0].upper() if login else "?"

    with st.sidebar:
        with st.expander(f"👤  {login}  ({emoji_role} {label_role})", expanded=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                <div style="width: 44px; height: 44px; border-radius: 50%;
                    background: #E63946; color: white; display: flex;
                    align-items: center; justify-content: center;
                    font-weight: 800; font-size: 1.1rem; flex-shrink: 0;">{initiale}</div>
                <div style="flex: 1;">
                    <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem;">{login}</div>
                    <div style="color: #FFD166; font-size: 0.78rem; font-weight: 600;">{emoji_role} {label_role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪  Se déconnecter", use_container_width=True, key=f"logout_{login}"):
                auth.deconnecter()
                st.rerun()


def sidebar_logout():
    pass


# ============================================================
# 📊 GRAPHIQUES SANS ANIMATION (v3 - CORRIGÉ)
# ============================================================
def configurer_graphique(fig, hauteur=350):
    """
    Configure un graphique Plotly SANS AUCUNE animation.
    Fonctionne avec go.Figure ET px (Plotly Express).
    ⚠️ NE PAS appeler fig.update_traces() ici (erreur sur Python 3.14).
    """
    fig.update_layout(
        height=hauteur,
        margin=dict(l=40, r=40, t=30, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1D3557"),
        transition=dict(duration=0, easing="linear"),
        uirevision="static",
    )
    return fig


def afficher_graphique(fig, hauteur=350):
    """
    Affiche un graphique Plotly SANS AUCUNE animation.
    À utiliser à la place de st.plotly_chart().
    """
    configurer_graphique(fig, hauteur)

    plotly_config = {
        "displayModeBar": False,
        "staticPlot": False,
        "responsive": True,
        "scrollZoom": False,
        "doubleClick": False,
        "showTips": False,
        "displaylogo": False,
        "transitionDuration": 0,
    }

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)


# ============================================================
# 🧩 COMPOSANTS
# ============================================================
def kpi_card(icon, label, value, trend=None, trend_type="positive",
             tendance=None, couleur=None, **kwargs):
    if trend is None and tendance is not None:
        trend = tendance
    border_style = f"border-left: 5px solid {couleur} !important;" if couleur else ""
    trend_html = f'<span class="kpi-trend {trend_type}">{trend}</span>' if trend else ""
    st.markdown(f"""
    <div class="kpi-card" style="{border_style}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def article_card(titre, source="", date="", sentiment=None, url=None, **kwargs):
    titre_propre = nettoyer_html(titre)
    source_propre = nettoyer_html(source)
    date_propre = str(date or "").strip()
    if not titre_propre:
        titre_propre = "(Titre non disponible)"
    badge_html = ""
    if sentiment:
        sc = str(sentiment).lower().strip()
        if sc in ("positif", "negatif", "neutre"):
            badge_html = f'<span class="article-badge badge-{sc}">{sc}</span>'
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
        <div class="article-meta">{meta_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 🔗 ALIAS
# ============================================================
def appliquer_style():
    return apply_style()


def section_title(icone, titre, sous_titre=""):
    st.markdown(f"## {icone} {titre}")
    if sous_titre:
        st.caption(sous_titre)
    st.markdown("")


def page_header(titre, icone="", description="", badge=None):
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
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#6C757D; font-size:0.8rem; padding:1rem;'>"
        "🇹🇳 <b>TuniWatch</b> © 2026 — Observatoire des médias en Tunisie"
        "</div>",
        unsafe_allow_html=True
    )