"""
Configuration globale TuniWatch : favicon, page config
Etape J - Polish final
"""

import streamlit as st


# Informations de l'application
APP_NAME = "TuniWatch"
APP_TAGLINE = "Observatoire des médias tunisiens"
APP_ICON = "🇹🇳"
APP_VERSION = "1.0"
APP_AUTHOR = "Khadraoui Mongi"


def setup_page(page_title, page_icon="🇹🇳", layout="wide"):
    """
    Configuration standardisee pour toutes les pages.
    A appeler au debut de chaque page (avant tout autre st.*).
    """
    st.set_page_config(
        page_title=f"{page_title} — {APP_NAME}",
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
        menu_items={
            "About": f"""
            ### {APP_ICON} {APP_NAME}
            **{APP_TAGLINE}**
            
            Version {APP_VERSION} — © 2026 {APP_AUTHOR}
            
            ---
            Plateforme de monitoring des médias tunisiens : 
            collecte automatique, analyse multilingue (FR/AR/AR-TN/Arabizi), 
            détection de thèmes et analyse de sentiment.
            """
        }
    )