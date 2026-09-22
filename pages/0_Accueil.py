"""
Page Accueil - Presentation du projet TuniWatch
Version 1.2 - Chiffres réels dans toutes les cartes
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import cockpit_stats

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
# CHARGEMENT DES STATS (une seule fois pour toute la page)
# ============================================================
try:
    with st.spinner("Chargement des statistiques..."):
        kpis = cockpit_stats.kpis_globaux()
        stats_themes = cockpit_stats.stats_themes_rapide()
    donnees_ok = True
except Exception as e:
    donnees_ok = False
    erreur_msg = str(e)

# Petit utilitaire : récupérer le nb d'articles d'un thème
def nb_articles_theme(theme_key):
    if not donnees_ok or not stats_themes:
        return 0
    for item in stats_themes:
        if item.get("theme") == theme_key:
            return item.get("nb_articles", 0)
    return 0

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

st.markdown("#### 🎯 Nos 4 thèmes principaux — nombre d'articles détectés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    style.kpi_card(
        "⚖️", "Violence femmes",
        f"{nb_articles_theme('violence_femmes')}",
        tendance="articles",
        couleur="#e74c3c"
    )
    st.caption("Violence conjugale, harcèlement, féminicide")

with col2:
    style.kpi_card(
        "👩", "Présence femmes",
        f"{nb_articles_theme('presence_femmes')}",
        tendance="articles",
        couleur="#9b59b6"
    )
    st.caption("Parité, représentation politique et économique")

with col3:
    style.kpi_card(
        "🗺️", "Équilibre régional",
        f"{nb_articles_theme('equilibre_regional')}",
        tendance="articles",
        couleur="#27ae60"
    )
    st.caption("Couverture équitable des régions")

with col4:
    style.kpi_card(
        "🏛️", "Équilibre politique",
        f"{nb_articles_theme('equilibre_politique')}",
        tendance="articles",
        couleur="#2c3e50"
    )
    st.caption("Représentation des partis et personnalités")

# ============================================================
# METHODOLOGIE
# ============================================================
style.section_title("🔬", "Méthodologie", "Comment nous collectons et analysons les données")

col1, col2, col3, col4 = st.columns(4)

nb_sources = kpis["total_sources"] if donnees_ok else "—"
nb_analyses = kpis["total_analyses_themes"] if donnees_ok else "—"
nb_mots = 456  # Nombre de mots-clés configurés (peut être dynamique plus tard)

with col1:
    style.kpi_card("1️⃣", "Sources collectées", nb_sources, couleur="#3498db")
    st.caption("📰 Presse RSS\n📻 11 Radios\n📺 TV & réseaux sociaux")

with col2:
    style.kpi_card("2️⃣", "Langues analysées", "4", couleur="#9b59b6")
    st.caption("🇫🇷 Français\n🇹🇳 Arabe standard\n🗣️ Arabe tunisien")

with col3:
    style.kpi_card("3️⃣", "Mots-clés actifs", f"{nb_mots}", couleur="#f39c12")
    st.caption("Répartis sur 7 thèmes de suivi")

with col4:
    style.kpi_card("4️⃣", "Analyses effectuées", nb_analyses, couleur="#27ae60")
    st.caption("Chiffres, évolution, comparaison")

# ============================================================
# CHIFFRES CLES (vue synthétique)
# ============================================================
style.section_title("📊", "Chiffres clés", "Données actuelles de l'observatoire")

if donnees_ok:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        style.kpi_card(
            "📰", "Articles collectés",
            f"{kpis['total_articles']:,}".replace(",", " "),
            couleur="#e70013"
        )

    with col2:
        style.kpi_card(
            "📡", "Sources actives",
            kpis["total_sources"],
            couleur="#3498db"
        )

    with col3:
        style.kpi_card(
            "🎯", "Analyses thèmes",
            kpis["total_analyses_themes"],
            couleur="#f39c12"
        )

    with col4:
        style.kpi_card(
            "💭", "Analyses sentiments",
            kpis["total_analyses_sentiment"],
            couleur="#27ae60"
        )
else:
    st.warning(f"⚠️ Impossible de charger les statistiques : {erreur_msg}")

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