"""
Page Accueil - Presentation du projet TuniWatch
Version 1.1 - Visuel premium
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style

# Configuration
st.set_page_config(
    page_title="Accueil - TuniWatch",
    page_icon="🏠",
    layout="wide"
)

# Style
style.appliquer_style()

# Protection
auth.require_login()

# ============================================================
# EN-TETE PREMIUM
# ============================================================
style.page_header(
    titre="TuniWatch",
    icone="🇹🇳",
    description="Observatoire des médias tunisiens — Analyse automatique de la représentation et des discours médiatiques",
    badge="v1.0"
)

# ============================================================
# PRESENTATION
# ============================================================
style.section_title("📖", "À propos", "Notre mission et nos sujets d'analyse")

st.markdown(
    """
    **TuniWatch** est un observatoire automatique qui analyse en continu 
    les contenus des médias tunisiens (presse, radios, TV) et des réseaux sociaux.
    
    Nous mesurons, documentons et rendons visible la représentation médiatique 
    des **sujets sociétaux** en Tunisie.
    """
)

st.markdown("#### 🎯 Nos 4 thèmes principaux")

col1, col2, col3, col4 = st.columns(4)

with col1:
    style.kpi_card("⚖️", "Violence femmes", "Suivi", couleur="#e74c3c")
    st.caption("Violence conjugale, harcèlement, féminicide")

with col2:
    style.kpi_card("👩", "Présence femmes", "Suivi", couleur="#9b59b6")
    st.caption("Parité, représentation politique et économique")

with col3:
    style.kpi_card("🗺️", "Équilibre régional", "Suivi", couleur="#27ae60")
    st.caption("Couverture équitable des régions")

with col4:
    style.kpi_card("🏛️", "Équilibre politique", "Suivi", couleur="#2c3e50")
    st.caption("Représentation des partis et personnalités")

# ============================================================
# METHODOLOGIE
# ============================================================
style.section_title("🔬", "Méthodologie", "Comment nous collectons et analysons les données")

col1, col2, col3, col4 = st.columns(4)

with col1:
    style.kpi_card("1️⃣", "Collecte", "Auto", couleur="#3498db")
    st.caption("📰 Presse RSS\n📻 11 Radios\n📺 TV & réseaux sociaux")

with col2:
    style.kpi_card("2️⃣", "Analyse", "Multi", couleur="#9b59b6")
    st.caption("🇫🇷 Français\n🇹🇳 Arabe standard\n🗣️ Arabe tunisien")

with col3:
    style.kpi_card("3️⃣", "Classification", "456", couleur="#f39c12")
    st.caption("Mots-clés répartis sur 7 thèmes")

with col4:
    style.kpi_card("4️⃣", "Visualisation", "Stats", couleur="#27ae60")
    st.caption("Chiffres, évolution, comparaison")

# ============================================================
# CHIFFRES CLES
# ============================================================
style.section_title("📊", "Chiffres clés", "Données actuelles de l'observatoire")

try:
    import analyzer
    import collector_ui

    conn = analyzer.get_connexion()
    curseur = conn.cursor(dictionary=True)

    curseur.execute("SELECT COUNT(*) AS nb FROM articles")
    nb_articles = curseur.fetchone()["nb"]

    curseur.execute("SELECT COUNT(*) AS nb FROM sources WHERE actif = 1")
    nb_sources = curseur.fetchone()["nb"]

    curseur.execute("SELECT COUNT(*) AS nb FROM mots_cles WHERE actif = 1")
    nb_mots = curseur.fetchone()["nb"]

    curseur.execute("SELECT COUNT(*) AS nb FROM articles_themes")
    nb_analyses = curseur.fetchone()["nb"]

    curseur.close()
    conn.close()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        style.kpi_card("📰", "Articles collectés",
                       f"{nb_articles:,}".replace(",", " "),
                       couleur="#e70013")

    with col2:
        style.kpi_card("📡", "Sources actives", nb_sources, couleur="#3498db")

    with col3:
        style.kpi_card("🔑", "Mots-clés", nb_mots, couleur="#f39c12")

    with col4:
        style.kpi_card("🎯", "Analyses effectuées", nb_analyses, couleur="#27ae60")

except Exception as e:
    st.warning(f"Impossible de charger les statistiques : {e}")

# ============================================================
# LIMITES ET ETHIQUE
# ============================================================
style.section_title("⚠️", "Limites et éthique", "Notre engagement de transparence")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 🎯 Limites")
    st.markdown(
        """
        - Les analyses reflètent **uniquement** les sources collectées
        - Les scores sont **indicatifs** et non des vérités absolues
        - La détection automatique peut générer des **faux positifs**
        - Le contexte **humain** reste indispensable pour interpréter
        """
    )

with col2:
    st.markdown("##### ⚖️ Éthique")
    st.markdown(
        """
        - **Aucune donnée personnelle** n'est collectée
        - Tous les articles sont **publics**
        - L'observatoire **respecte les CGU** des sources
        - Les résultats sont **transparents** et **vérifiables**
        """
    )

# ============================================================
# CREDITS ET CONTACT
# ============================================================
style.section_title("👤", "Contact", "Informations sur le projet")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **Développé par** : Khadraoui Mongi  
        **Année** : 2026  
        **Version** : 1.0  
        """
    )

with col2:
    st.markdown(
        f"""
        **Dernière mise à jour** : {datetime.now().strftime('%d/%m/%Y')}  
        **Statut** : 🟢 En développement actif  
        """
    )

# ============================================================
# CALL TO ACTION
# ============================================================
st.markdown("---")
st.success(
    "💡 **Bienvenue sur TuniWatch !** Utilisez le menu à gauche pour explorer les analyses."
)

# Footer
style.footer()