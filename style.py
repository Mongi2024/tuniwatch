"""
Module style.py - Style CSS personnalise TuniWatch
Version 0.5 - Version finale stable
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
}

ORDRE_AFFICHAGE = ["0", "1", "3", "8", "9", "10", "12", "11", "7", "6", "4", "2", "5"]


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

        # Dashboard
        if st.button("🏠  Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("dashboard.py")

        # Autres pages
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