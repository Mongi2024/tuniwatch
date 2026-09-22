"""
Page Accueil - Vitrine TuniWatch
Version 2.0 - Présentation chiffrée de l'observatoire
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    page_icon="🇹🇳",
    layout="wide"
)

# Style
style.appliquer_style()

# Protection
auth.require_login()

# ============================================================
# COULEURS THEMES
# ============================================================
COULEURS_THEMES = {
    "violence_femmes": "#e74c3c",
    "discours_haine": "#c0392b",
    "presence_femmes": "#9b59b6",
    "presence_handicapes": "#3498db",
    "presence_jeunes": "#f39c12",
    "equilibre_politique": "#2c3e50",
    "equilibre_regional": "#27ae60"
}

EMOJIS_THEMES = {
    "violence_femmes": "⚖️",
    "discours_haine": "🚨",
    "presence_femmes": "👩",
    "presence_handicapes": "👥",
    "presence_jeunes": "🧑",
    "equilibre_politique": "🏛️",
    "equilibre_regional": "🗺️"
}

# ============================================================
# EN-TETE
# ============================================================
style.page_header(
    titre="Bienvenue sur TuniWatch",
    icone="🇹🇳",
    description="Observatoire automatique des médias et réseaux sociaux tunisiens — Suivi en temps réel de la représentation médiatique",
    badge="LIVE"
)

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================
try:
    with st.spinner("Chargement des données..."):
        kpis = cockpit_stats.kpis_globaux()
        sentiment = cockpit_stats.stats_sentiment()
        erreur_chargement = False
except Exception as e:
    erreur_chargement = True
    erreur_msg = str(e)

if erreur_chargement:
    st.error(f"⚠️ Impossible de charger les données : {erreur_msg}")
    st.info("Vérifiez la connexion à la base de données dans `cockpit_stats.py`.")
    st.stop()

# ============================================================
# SECTION 1 : CHIFFRES CLES (EN GROS)
# ============================================================
style.section_title(
    "📊",
    "L'observatoire en chiffres",
    "Données collectées automatiquement en continu"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    trend = f"+{kpis['total_articles'] - 411}" if kpis['total_articles'] > 411 else None
    style.kpi_card(
        "📰", "Articles collectés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        tendance=trend,
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

# ============================================================
# SECTION 2 : APERCU GRAPHIQUE (2 mini-graphes pour donner envie)
# ============================================================
style.section_title(
    "📈",
    "Aperçu des tendances",
    "Un extrait des analyses disponibles — voir le Dashboard pour plus de détails"
)

col1, col2 = st.columns([2, 1])

# --- Courbe évolution ---
with col1:
    st.markdown("##### 📈 Évolution des mentions (30 derniers jours)")

    evolution = cockpit_stats.evolution_mentions(30)

    if evolution:
        df_evol = pd.DataFrame(evolution)

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(
            x=df_evol["jour"],
            y=df_evol["nb"],
            mode="lines",
            line=dict(color="#e70013", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(231, 0, 19, 0.08)",
            hovertemplate="<b>%{x}</b><br>%{y} articles<extra></extra>"
        ))
        fig_evol.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showline=True, linecolor="#e0e0e0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0", showline=False),
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution disponible.")

# --- Donut sentiment ---
with col2:
    st.markdown("##### 😊 Sentiment global")

    total_sent = (
        (sentiment.get("positifs", 0) or 0)
        + (sentiment.get("neutres", 0) or 0)
        + (sentiment.get("negatifs", 0) or 0)
    )

    if total_sent > 0:
        fig_sent = go.Figure(data=[go.Pie(
            labels=["Positifs", "Neutres", "Négatifs"],
            values=[
                sentiment.get("positifs", 0) or 0,
                sentiment.get("neutres", 0) or 0,
                sentiment.get("negatifs", 0) or 0
            ],
            hole=0.6,
            marker=dict(colors=["#27ae60", "#f39c12", "#e74c3c"]),
            textinfo="percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>"
        )])
        fig_sent.update_layout(
            showlegend=True,
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                        xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("Aucune donnée de sentiment.")

# ============================================================
# SECTION 3 : LES 4 THEMES AVEC LEURS VRAIS CHIFFRES
# ============================================================
style.section_title(
    "🎯",
    "Les 4 thèmes surveillés",
    "Représentation médiatique des sujets sociétaux en Tunisie"
)

stats_themes = cockpit_stats.stats_themes_rapide()

if stats_themes:
    df_themes = pd.DataFrame(stats_themes)

    # Dictionnaire des infos descriptives de chaque thème
    THEMES_INFO = {
        "violence_femmes": {
            "nom": "Violence envers les femmes",
            "desc": "Violence conjugale, harcèlement, féminicide",
            "couleur": "#e74c3c",
            "emoji": "⚖️"
        },
        "presence_femmes": {
            "nom": "Présence des femmes",
            "desc": "Parité, représentation politique et économique",
            "couleur": "#9b59b6",
            "emoji": "👩"
        },
        "equilibre_regional": {
            "nom": "Équilibre régional",
            "desc": "Couverture équitable de toutes les régions",
            "couleur": "#27ae60",
            "emoji": "🗺️"
        },
        "equilibre_politique": {
            "nom": "Équilibre politique",
            "desc": "Représentation des partis et personnalités",
            "couleur": "#2c3e50",
            "emoji": "🏛️"
        },
    }

    col1, col2, col3, col4 = st.columns(4)

    # Ordre d'affichage souhaité
    ordre = ["violence_femmes", "presence_femmes",
             "equilibre_regional", "equilibre_politique"]

    for idx, (col, theme_key) in enumerate(zip(
        [col1, col2, col3, col4], ordre
    )):
        info = THEMES_INFO.get(theme_key)
        if not info:
            continue

        # Récupérer le nombre d'articles pour ce thème
        ligne = df_themes[df_themes["theme"] == theme_key]
        nb = int(ligne["nb_articles"].iloc[0]) if not ligne.empty else 0

        with col:
            style.kpi_card(
                info["emoji"],
                info["nom"],
                f"{nb}",
                tendance="articles",
                couleur=info["couleur"]
            )
            st.caption(info["desc"])

# ============================================================
# SECTION 4 : CALL TO ACTION
# ============================================================
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0;">
            <h3 style="color: #1a1a1a; margin-bottom: 10px;">
                📊 Prêt à explorer les analyses ?
            </h3>
            <p style="color: #666; margin-bottom: 20px;">
                Consultez le Dashboard pour accéder à toutes les visualisations
                et analyses détaillées.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🏠 Aller au Dashboard", use_container_width=True, type="primary"):
        st.switch_page("dashboard.py")

# ============================================================
# SECTION 5 : A PROPOS (repliable)
# ============================================================
with st.expander("ℹ️ À propos de TuniWatch — Méthodologie, éthique et contact"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 🎯 Notre mission
            
            **TuniWatch** est un observatoire automatique qui analyse en continu 
            les contenus des médias tunisiens (presse, radios, TV) et des réseaux sociaux.
            
            Nous mesurons, documentons et rendons visible la **représentation médiatique**
            des sujets sociétaux en Tunisie.
            
            ### 🔬 Méthodologie
            
            1. **Collecte automatique** — RSS presse, radios, TV
            2. **Analyse multilingue** — 🇫🇷 FR, 🇹🇳 AR standard, 🗣️ AR tunisien, Arabizi
            3. **Classification** — 456 mots-clés sur 7 thèmes
            4. **Visualisation** — Statistiques et comparaisons exploitables
            """
        )

    with col2:
        st.markdown(
            """
            ### ⚠️ Limites
            
            - Analyses basées **uniquement** sur les sources collectées
            - Les scores sont **indicatifs**, non des vérités absolues
            - La détection automatique peut générer des **faux positifs**
            - Le contexte **humain** reste indispensable
            
            ### ⚖️ Éthique
            
            - **Aucune donnée personnelle** collectée
            - Tous les articles sont **publics**
            - **Respect des CGU** des sources
            - Résultats **transparents** et **vérifiables**
            
            ### 👤 Contact
            
            **Développé par** : Khadraoui Mongi  
            **Année** : 2026 — **Version** : 1.0
            """
        )

# Footer
style.footer()