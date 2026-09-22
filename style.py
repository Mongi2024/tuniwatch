"""
Module style.py - Style CSS personnalise TuniWatch
Version 0.7 - Ajout page Médias (13) dans la navigation
"""

import streamlit as st
import os


# ============================================================
# COULEURS TUNIWATCH
# ============================================================
COULEUR_PRIMAIRE = "#e70013"
COULEUR_PRIMAIRE_DARK = "#b8000f"
COULEUR_ACCENT = "#1a1a1a"


# ============================================================
# CONFIGURATION DES PAGES
# ============================================================
PAGES_CONFIG = {
    "0":  ("ℹ️", "Accueil", "all"),
    "1":  ("📊", "Analyse", "all"),
    "2":  ("⚙️", "Admin", "super_admin"),
    "3":  ("📰", "Actualités", "all"),
    "4":  ("👤", "Profil", "all"),
    "5":  ("👥", "Utilisateurs", "super_admin"),
    "6":  ("📝", "Mots Clés", "all"),
    "7":  ("📡", "Sources", "all"),
    "8":  ("🎯", "Thèmes", "all"),
    "9":  ("💭", "Sentiments", "all"),
    "10": ("🚨", "Alertes", "all"),
    "11": ("📄", "Rapport", "all"),
    "12": ("🔍", "Recherche", "all"),
    "13": ("📺", "Médias", "all"),
}

ORDRE_AFFICHAGE = ["0", "1", "3", "8", "9", "10", "12", "11", "7", "13", "6", "4", "2", "5"]


def _scanner_pages():
    """Scanne le dossier pages/ pour trouver les fichiers reels."""
    pages_trouvees = {}
    dossier_pages = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
    if not os.path.exists(dossier_pages):
        return pages_trouvees
    for fichier in os.listdir(dossier_pages):
        if not fichier.endswith(".py"):
            continue
        parties = fichier.split("_", 1)
        if len(parties) < 2:
            continue
        prefixe = parties[0]
        pages_trouvees[prefixe] = f"pages/{fichier}"
    return pages_trouvees


def appliquer_style():
    """Applique le CSS + ajoute la sidebar automatique."""
    css = """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        h1 {
            color: #1a1a1a !important;
            font-weight: 700 !important;
            border-bottom: 3px solid #e70013 !important;
            padding-bottom: 10px !important;
        }
        h2 {
            color: #1a1a1a !important;
            font-weight: 600 !important;
            margin-top: 1.5rem !important;
        }
        h3 {
            color: #1a1a1a !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
            border-right: 3px solid #e70013;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            color: #1a1a1a;
            border: 1.5px solid #e0e0e0;
            font-weight: 600;
            padding: 10px 14px;
            text-align: left;
            transition: all 0.2s ease;
            border-radius: 8px;
            width: 100%;
            margin-bottom: 4px;
            font-size: 0.92rem;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, #e70013 0%, #b8000f 100%);
            color: white !important;
            border-color: #e70013;
            transform: translateX(4px);
            box-shadow: 0 3px 10px rgba(231, 0, 19, 0.3);
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #e70013 0%, #b8000f 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            box-shadow: 0 3px 10px rgba(231, 0, 19, 0.25) !important;
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #b8000f 0%, #900008 100%) !important;
            transform: translateY(-2px) !important;
        }
        [data-testid="stMetricValue"] {
            color: #e70013 !important;
            font-weight: 700 !important;
        }
        .main .stButton > button[kind="primary"] {
            background-color: #e70013 !important;
            border-color: #e70013 !important;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus {
            border-color: #e70013 !important;
            box-shadow: 0 0 0 2px rgba(231, 0, 19, 0.1) !important;
        }
        .tuniwatch-footer {
            text-align: center;
            padding: 20px 0;
            color: #666;
            font-size: 0.85rem;
            border-top: 1px solid #e0e0e0;
            margin-top: 40px;
        }
        .stDeployButton {
            display: none !important;
        }
        #MainMenu {
            visibility: hidden;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main .block-container {
            animation: fadeIn 0.3s ease-in;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    _afficher_header_sidebar()
    _afficher_navigation()


def _afficher_header_sidebar():
    """Affiche logo TuniWatch + carte utilisateur."""
    user = st.session_state.get("user")
    if not user:
        return

    role = user.get("role", "viewer")
    emojis_role = {"super_admin": "👑", "admin": "🔑", "viewer": "👤"}
    labels_role = {
        "super_admin": "Super Admin",
        "admin": "Administrateur",
        "viewer": "Lecteur"
    }
    emoji = emojis_role.get(role, "👤")
    label = labels_role.get(role, role)
    initiale = (user.get("login") or "?")[0].upper()

    with st.sidebar:
        logo_html = '<div style="text-align: center; padding: 15px 0 10px 0;">'
        logo_html += '<div style="font-size: 2.5rem; line-height: 1;">🇹🇳</div>'
        logo_html += '<div style="font-size: 1.4rem; font-weight: 800; color: #e70013; margin-top: 8px; letter-spacing: 0.5px;">TuniWatch</div>'
        logo_html += '<div style="font-size: 0.72rem; color: #888; margin-top: 2px;">Observatoire des médias</div>'
        logo_html += '</div>'
        st.markdown(logo_html, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 12px 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)

        user_html = '<div style="background: linear-gradient(135deg, #e70013 0%, #b8000f 100%); border-radius: 12px; padding: 14px; color: white; box-shadow: 0 4px 12px rgba(231, 0, 19, 0.3); margin-bottom: 10px;">'
        user_html += '<div style="display: flex; align-items: center; gap: 12px;">'
        user_html += f'<div style="width: 44px; height: 44px; background: rgba(255,255,255,0.25); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; flex-shrink: 0;">{initiale}</div>'
        user_html += '<div style="flex: 1; overflow: hidden;">'
        user_html += f'<div style="font-weight: 700; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user.get("login", "Utilisateur")}</div>'
        user_html += f'<div style="font-size: 0.72rem; opacity: 0.9; margin-top: 2px;">{emoji} {label}</div>'
        user_html += '</div></div></div>'
        st.markdown(user_html, unsafe_allow_html=True)


def _afficher_navigation():
    """Affiche le menu dynamique."""
    import auth

    user = st.session_state.get("user")
    if not user:
        return

    role = user.get("role", "viewer")
    pages_reelles = _scanner_pages()

    with st.sidebar:
        st.markdown('<div style="font-size: 0.75rem; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 15px 0 10px 0;">🧭 Navigation</div>', unsafe_allow_html=True)

        if st.button("🏠  Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("dashboard.py")

        for prefixe in ORDRE_AFFICHAGE:
            if prefixe not in PAGES_CONFIG:
                continue
            if prefixe not in pages_reelles:
                continue

            emoji, label, req_role = PAGES_CONFIG[prefixe]

            if req_role == "super_admin" and role != "super_admin":
                continue

            chemin = pages_reelles[prefixe]

            if st.button(f"{emoji}  {label}", use_container_width=True, key=f"nav_{prefixe}"):
                st.switch_page(chemin)

        st.markdown("<hr style='margin: 12px 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)

        if st.button("🚪  Se déconnecter", use_container_width=True, type="primary", key=f"logout_global_{user.get('login', 'user')}"):
            auth.deconnecter()
            st.rerun()

        st.markdown("<hr style='margin: 12px 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #aaa; font-size: 0.7rem; padding: 10px 0;">Version 1.0 — Cockpit<br>© 2026 Khadraoui Mongi</div>', unsafe_allow_html=True)


def footer():
    """Affiche un pied de page personnalise."""
    st.markdown('<div class="tuniwatch-footer">🇹🇳 <b>TuniWatch</b> — Observatoire des médias tunisiens<br>© 2026 Khadraoui Mongi — Tous droits réservés</div>', unsafe_allow_html=True)


def page_header(titre, icone, description, badge=None):
    """Affiche un en-tete uniforme pour toutes les pages."""
    badge_html = ""
    if badge:
        badge_html = f'<span style="background: linear-gradient(135deg, #e70013 0%, #b8000f 100%); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; margin-left: 12px; text-transform: uppercase; letter-spacing: 0.5px; vertical-align: middle;">{badge}</span>'

    html = '<div style="padding: 24px 0 20px 0; border-bottom: 3px solid #e70013; margin-bottom: 30px;">'
    html += '<h1 style="margin: 0; display: flex; align-items: center; gap: 15px; font-size: 2rem; color: #1a1a1a; border: none !important; padding: 0 !important;">'
    html += f'<span style="font-size: 2.4rem;">{icone}</span>'
    html += f'<span>{titre}</span>'
    html += badge_html
    html += '</h1>'
    html += f'<p style="margin: 8px 0 0 0; color: #666; font-size: 0.95rem; padding-left: 4px;">{description}</p>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# NOUVELLES FONCTIONS - Visuel Premium (concaténation)
# ============================================================

def kpi_card(icone, label, valeur, tendance=None, couleur=None):
    """Affiche une carte KPI moderne."""
    if couleur is None:
        couleur = "#e70013"

    if tendance:
        trend_html = (
            '<div style="display: inline-block; background: rgba(39, 174, 96, 0.12); '
            'color: #27ae60; padding: 4px 10px; border-radius: 12px; '
            'font-size: 0.78rem; font-weight: 700; margin-top: 8px;">'
            f'↑ {tendance}'
            '</div>'
        )
    else:
        trend_html = ""

    html = (
        '<div style="'
        'background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%); '
        'border-radius: 14px; '
        'padding: 20px 22px; '
        'box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06); '
        f'border-left: 5px solid {couleur}; '
        'height: 100%; '
        'min-height: 130px;'
        '">'
        '<div style="'
        'font-size: 0.72rem; color: #6c757d; text-transform: uppercase; '
        'letter-spacing: 1.2px; font-weight: 600; margin-bottom: 10px;'
        '">'
        f'{icone} {label}'
        '</div>'
        '<div style="'
        'font-size: 2rem; font-weight: 800; color: #1a1a1a; '
        'line-height: 1.1; margin-bottom: 4px;'
        '">'
        f'{valeur}'
        '</div>'
        f'{trend_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def article_card(titre, source, url, score=None, theme=None, emoji_theme="🌐"):
    """Affiche une carte d'article élégante."""
    if score is not None:
        if score >= 6:
            score_color = "#27ae60"
            score_bg = "rgba(39, 174, 96, 0.12)"
        elif score >= 4:
            score_color = "#f39c12"
            score_bg = "rgba(243, 156, 18, 0.12)"
        else:
            score_color = "#95a5a6"
            score_bg = "rgba(149, 165, 166, 0.12)"

        score_html = (
            '<span style="'
            f'background: {score_bg}; color: {score_color}; '
            'padding: 3px 10px; border-radius: 10px; '
            'font-size: 0.72rem; font-weight: 700; margin-left: 8px;'
            '">'
            f'{score:.2f}'
            '</span>'
        )
    else:
        score_html = ""

    if theme:
        theme_html = (
            '<span style="'
            'background: rgba(231, 0, 19, 0.08); color: #e70013; '
            'padding: 3px 10px; border-radius: 10px; '
            'font-size: 0.7rem; font-weight: 600; margin-left: 6px;'
            '">'
            f'{emoji_theme} {theme}'
            '</span>'
        )
    else:
        theme_html = ""

    if url:
        lien = (
            f'<a href="{url}" target="_blank" style="'
            'color: #1a1a1a; text-decoration: none; '
            'font-weight: 600; font-size: 0.92rem; line-height: 1.4;'
            '">'
            f'{titre}'
            '</a>'
        )
    else:
        lien = (
            '<span style="'
            'font-weight: 600; font-size: 0.92rem; color: #1a1a1a;'
            '">'
            f'{titre}'
            '</span>'
        )

    html = (
        '<div style="'
        'background: #ffffff; '
        'border-radius: 12px; '
        'padding: 16px 18px; '
        'margin-bottom: 12px; '
        'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); '
        'border-left: 4px solid #e70013;'
        '">'
        '<div style="margin-bottom: 8px;">'
        f'{lien} {score_html}'
        '</div>'
        '<div style="font-size: 0.78rem; color: #888;">'
        f'📰 {source} {theme_html}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_title(icone, titre, sous_titre=None):
    """Affiche un titre de section élégant."""
    html = (
        '<div style="margin: 30px 0 20px 0;">'
        '<h2 style="'
        'margin: 0; font-size: 1.4rem; color: #1a1a1a; '
        'font-weight: 700; display: flex; align-items: center; '
        'gap: 10px; border: none; padding: 0;'
        '">'
        f'<span style="font-size: 1.6rem;">{icone}</span>'
        f'<span>{titre}</span>'
        '</h2>'
    )
    if sous_titre:
        html += (
            '<p style="'
            'margin: 6px 0 0 40px; color: #888; font-size: 0.88rem;'
            '">'
            f'{sous_titre}'
            '</p>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)