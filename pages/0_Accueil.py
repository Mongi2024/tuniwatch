"""
Page Accueil - Presentation du projet TuniWatch
Etape E - Session 1
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
# EN-TETE
# ============================================================
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 5rem;">🇹🇳</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.title("TuniWatch")
    st.markdown("### Observatoire des médias tunisiens")
    st.caption("Analyse automatique de la représentation et des discours médiatiques")

st.markdown("---")

# ============================================================
# PRESENTATION
# ============================================================
st.markdown("""
## 📖 À propos

**TuniWatch** est un observatoire automatique qui analyse en continu 
les contenus des médias tunisiens (presse, radios, TV) et des réseaux sociaux.

### 🎯 Notre mission

Mesurer, documenter et rendre visible la représentation médiatique des 
**sujets sociétaux** en Tunisie :
""")

col1, col2, col3, col4 = st.columns(4)

themes = [
    ("⚖️", "Violence femmes", "Violence conjugale, harcèlement, féminicide"),
    ("👩", "Présence femmes", "Parité, représentation politique et économique"),
    ("🗺️", "Équilibre régional", "Couverture équitable des régions"),
    ("🏛️", "Équilibre politique", "Représentation des partis et personnalités"),
]

with col1:
    st.markdown("""
    <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px; height: 150px;">
        <div style="font-size: 2rem;">⚖️</div>
        <b>Violence femmes</b><br>
        <small style="color: #666;">Violence conjugale, harcèlement</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px; height: 150px;">
        <div style="font-size: 2rem;">👩</div>
        <b>Présence femmes</b><br>
        <small style="color: #666;">Parité, représentation</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px; height: 150px;">
        <div style="font-size: 2rem;">🗺️</div>
        <b>Équilibre régional</b><br>
        <small style="color: #666;">Couverture équitable des régions</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px; height: 150px;">
        <div style="font-size: 2rem;">🏛️</div>
        <b>Équilibre politique</b><br>
        <small style="color: #666;">Partis et personnalités</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# METHODOLOGIE
# ============================================================
st.markdown("## 🔬 Méthodologie")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 1️⃣ Collecte
    Articles récupérés automatiquement depuis :
    - 📰 Presse tunisienne (RSS)
    - 📻 Radios (11 radios nationales et régionales)
    - 📺 TV, réseaux sociaux
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Analyse
    Traitement multilingue :
    - 🇫🇷 Français
    - 🇹🇳 Arabe standard (فصحى)
    - 🗣️ Arabe tunisien (دارجة)
    - 🔤 Arabizi
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Classification
    456 mots-clés répartis sur 7 thèmes détectent automatiquement la présence des sujets surveillés.
    """)

with col4:
    st.markdown("""
    ### 4️⃣ Visualisation
    Statistiques exploitables :
    - Chiffres par thème
    - Évolution temporelle
    - Comparaison médias
    """)

st.markdown("---")

# ============================================================
# CHIFFRES CLES
# ============================================================
st.markdown("## 📊 Chiffres clés")

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
    col1.metric("📰 Articles collectés", f"{nb_articles:,}".replace(",", " "))
    col2.metric("📡 Sources actives", nb_sources)
    col3.metric("🔑 Mots-clés", nb_mots)
    col4.metric("🎯 Analyses effectuées", nb_analyses)

except Exception as e:
    st.warning(f"Impossible de charger les statistiques : {e}")

st.markdown("---")

# ============================================================
# LIMITES ET ETHIQUE
# ============================================================
st.markdown("## ⚠️ Limites et éthique")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 Limites
    
    - Les analyses reflètent **uniquement** les sources collectées
    - Les scores sont **indicatifs** et non des vérités absolues
    - La détection automatique peut générer des **faux positifs**
    - Le contexte **humain** reste indispensable pour interpréter
    """)

with col2:
    st.markdown("""
    ### ⚖️ Éthique
    
    - **Aucune donnée personnelle** n'est collectée
    - Tous les articles sont **publics**
    - L'observatoire **respecte les CGU** des sources
    - Les résultats sont **transparents** et **vérifiables**
    """)

st.markdown("---")

# ============================================================
# CREDITS
# ============================================================
st.markdown("## 👤 Contact")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Développé par** : Khadraoui Mongi  
    **Année** : 2026  
    **Version** : 1.0  
    """)

with col2:
    st.markdown(f"""
    **Dernière mise à jour** : {datetime.now().strftime('%d/%m/%Y')}  
    **Statut** : 🟢 En développement actif  
    """)

st.markdown("---")

# ============================================================
# CALL TO ACTION
# ============================================================
st.success("""
💡 **Bienvenue sur TuniWatch !** Utilisez le menu à gauche pour explorer les analyses.
""")

# Footer
style.footer()